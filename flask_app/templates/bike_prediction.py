from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, DublinBike
from config import MySQL
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

host = MySQL.host
user = MySQL.username
password = MySQL.password
database = MySQL.database

engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
Base.metadata.create_all(engine)

session = sessionmaker()
session.configure(bind=engine)
s = session()

query_bike = "SELECT *\
         FROM dublin_bike"

query_weather = "SELECT *\
         FROM current_weather\
         WHERE number = %(number)s"

bike_df = pd.read_sql_table(table_name="dublin_bike", schema="development",  con=engine, parse_dates=['scraping_time'])
weather_df = pd.read_sql_table(table_name="current_weather", schema="development",  con=engine, parse_dates=['scraping_time'])
weather_df.to_pickle("./weather_df.pkl")
bike_df.to_pickle("./bike_df.pkl")
# bike_df = pd.read_pickle("./bike_df.pkl")
bike_df.head(10)
# weather_df = pd.read_pickle("./weather_df.pkl")
print(bike_df.head(10))








