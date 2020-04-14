import datetime
import pandas as pd
import numpy as np


def bike_predict_daily(number_input, engine, model):
    # Calibrate the query ata amount by current time
    hour_left = 2016 - datetime.datetime.utcnow().hour

    query_bike = "SELECT * \
                  FROM development.dublin_bike\
                  WHERE number = %(number)s\
                  ORDER BY scraping_time desc\
                  LIMIT %(size)s;"

    query_weather = "SELECT * \
                    FROM development.current_weather\
                    WHERE stationNum = %(number)s \
                    ORDER BY datetime desc\
                    LIMIT %(size)s;"

    bike_df = pd.read_sql_query(sql=query_bike, con=engine, params={'number': number_input, 'size': hour_left},
                                parse_dates=['scraping_time'])
    weather_df = pd.read_sql_query(sql=query_weather, con=engine, params={'number': number_input, 'size': hour_left},
                                   parse_dates=['scraping_time'])

    '''Add label'''
    def labeling_eval(df):
        df["available_bike_ratio"] = df['available_bike'] / df['bike_stand']
        return df

    '''Merge weather and bike table'''
    def merge_df(bike_df, weather_df):
        combined_df = pd.merge(bike_df, weather_df, how='inner',
                               left_on=['number', 'scraping_time'],
                               right_on=['stationNum', 'datetime'],
                               suffixes=('_bike', '_weather'))
        return combined_df

    '''Extract hour of the day'''
    def datetime_conversion(df, df_col):
        df['hour'] = df[df_col].dt.hour
        return df

    '''Feature engineeer the time feature to cyclic sine cosine representation'''
    def time_transform(df, col, max_val):
        df[col + '_sin'] = np.sin(2 * np.pi * df[col] / max_val)
        df[col + '_cos'] = np.cos(2 * np.pi * df[col] / max_val)
        df = df.drop([col], axis=1)
        return df

    '''Drop redundant columns'''
    def data_cleaning(df):
        pd.set_option('display.max_columns', 500)
        col_to_drop = ['address', 'site_names', 'bonus', 'last_update', 'datetime', 'icon', 'lon', 'lat', 'stationNum',
                       'available_bike_stand', 'description', 'status', 'sunset']
        df = df.drop(col_to_drop, axis=1)
        df = df.drop_duplicates().reset_index()
        df = df.drop(['index'], axis=1)
        df = df.drop(['available_bike'], axis=1)

        return df

    '''Convert data type'''
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
    daily_df = combined_df.resample('H', on='scraping_time').mean().sort_values('hour').reset_index()

    weekday = (7 - ((8 - daily_df['weekday']) % 7)).astype('int32')
    hour = daily_df['hour'].astype('int32')
    daily_df = time_transform(daily_df, 'weekday', 7)
    daily_df = time_transform(daily_df, 'hour', 23)
    daily_df.drop('scraping_time', axis=1, inplace=True)
    total_bike_stand = combined_df.loc[0, 'bike_stand']

    # Inference with model
    y_prediction = model.predict(daily_df)

    # Reformat the data to json format
    data = pd.DataFrame({'number': daily_df['number'], 'hour': hour, 'weekday': weekday,
                         'bike_predict': y_prediction * total_bike_stand})
    days = {1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat', 7: 'Sun'}
    data['weekday'] = data['weekday'].apply(lambda x: days[x])
    data = data.set_index(['weekday'])
    predict_daily_json = {}

    # Combine json data
    for i in data.index:
        predict_daily_json[i] = data.loc[i, ['number', 'hour', 'bike_predict']].to_dict(orient='records')

    return predict_daily_json
