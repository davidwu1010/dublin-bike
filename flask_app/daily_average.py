from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base
from config import MySQL
import pandas as pd


engine = create_engine(MySQL.URI)
Base.metadata.create_all(engine)

session = sessionmaker()
session.configure(bind=engine)
s = session()


def get_daily_mean_json(number_input):
    query = "SELECT scraping_time, number, address,\
             site_names, latitude, longitude,\
             bike_stand, available_bike_stand,available_bike\
             FROM dublin_bike\
             WHERE number = %(number)s"

    df = pd.read_sql_query(sql=query,
                           con=engine,
                           params={'number': number_input},
                           parse_dates=['scraping_time'])

    df["day_of_week"] = df["scraping_time"].dt.dayofweek

    day_mean = df.groupby("day_of_week").mean().reset_index()\
        .sort_values("day_of_week")
    days = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat',
            6: 'Sun'}
    day_mean['day_of_week'] = day_mean['day_of_week'].apply(lambda x: days[x])

    return day_mean.to_json(orient='records')
