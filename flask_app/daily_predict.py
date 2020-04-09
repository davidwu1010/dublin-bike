
from sqlalchemy import create_engine
from models.schemas import Base
from config import MySQL
import pandas as pd
import numpy as np
import joblib

import joblib
def bike_predict_daily(number_input):
    host = MySQL.host
    user = MySQL.username
    password = MySQL.password
    database = MySQL.database

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    Base.metadata.create_all(engine)

    query_bike = "SELECT * \
                  FROM development.dublin_bike\
                  WHERE number = %(number)s\
                  ORDER BY scraping_time desc\
                  LIMIT 1728"

    query_weather = "SELECT * \
                    FROM development.current_weather\
                    WHERE stationNum =%(number)s \
                    ORDER BY datetime desc\
                    LIMIT 1728"

    bike_df = pd.read_sql_query(sql=query_bike, con=engine, params={'number': number_input},
                                parse_dates=['scraping_time'])
    weather_df = pd.read_sql_query(sql=query_weather, con=engine, params={'number': number_input},
                                   parse_dates=['scraping_time'])

    def labeling_eval(df):
        df["available_bike_ratio"] = df['available_bike'] / df['bike_stand']
        return df

    def merge_df(bike_df, weather_df):
        combined_df = pd.merge(bike_df, weather_df, how='inner',
                               left_on=['number', 'scraping_time'],
                               right_on=['stationNum', 'datetime'],
                               suffixes=('_bike', '_weather'))
        return combined_df

    def datetime_conversion(df, df_col):
        df['hour'] = df[df_col].dt.hour
        return df

    def time_transform(df, col, max_val):
        df[col + '_sin'] = np.sin(2 * np.pi * df[col] / max_val)
        df[col + '_cos'] = np.cos(2 * np.pi * df[col] / max_val)
        df = df.drop([col], axis=1)
        return df

    def data_cleaning(df):
        pd.set_option('display.max_columns', 500)
        col_to_drop = ['address', 'site_names', 'bonus', 'last_update', 'datetime', 'icon', 'lon', 'lat', 'stationNum',
                       'available_bike_stand', 'description', 'status', 'sunset']
        df = df.drop(col_to_drop, axis=1)
        df = df.drop_duplicates().reset_index()
        df = df.drop(['index'], axis=1)
        df = df.drop(['available_bike'], axis=1)

        return df

    def data_type_conversion(df):
        df['banking'] = df['banking'].astype('int32')
        df['code'] = df['code'].astype('int32') // 100
        df['temperature'] = df['temperature'].astype('float64')
        return df


    bike_df = labeling_eval(bike_df)
    combined_df = merge_df(bike_df, weather_df)

    combined_df = data_type_conversion(combined_df)
    combined_df = data_cleaning(combined_df)
    combined_df = datetime_conversion(combined_df, "scraping_time")
    daily_df = combined_df.resample('H', on='scraping_time').mean().reset_index()
    weekday = daily_df['weekday'].astype('int32')
    hour = daily_df['hour'].astype('int32')
    daily_df = time_transform(daily_df, 'weekday', 7)
    daily_df = time_transform(daily_df, 'hour', 23)
    daily_df.drop('scraping_time', axis=1, inplace =True)
    total_bike_stand = combined_df.loc[0,'bike_stand']

    model_name = 'lgbm_model_daily.pkl'
    model = joblib.load(model_name)
    y_prediction = model.predict(daily_df)
    data = pd.DataFrame({'number':daily_df['number'], 'hour': hour, 'weekday': weekday,
                         'bike_predict':y_prediction *total_bike_stand})
    days = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
    data['weekday'] = data['weekday'].apply(lambda x: days[x])
    data = data.set_index(['weekday'])
    predict_daily_json = {}
    for i in data.index:
        predict_daily_json[i] = data.loc['Fri',['number','hour','bike_predict']].to_dict(orient='records')

    return predict_daily_json


