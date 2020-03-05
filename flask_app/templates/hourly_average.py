
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

def create_chart(number_input ):

    query = "SELECT scraping_time, number, address,\
             site_names, latitude, longitude,\
             bike_stand, available_bike_stand,available_bike\
             FROM dublin_bike\
             WHERE number = %(number)s"

    df = pd.read_sql_query(sql=query,
                           con=engine,
                           params={'number': number_input},
                           parse_dates=['scraping_time'])

    df["hour"] = df["scraping_time"].dt.hour
    hourly_mean = df.groupby("hour").mean()

    capacity = df.loc[0,"bike_stand"]

    fig, ax = plt.subplots()
    plt.bar(list(hourly_mean.index), hourly_mean["available_bike"])
    plt.xticks(np.arange(0, 23, step=2))
    plt.yticks(np.arange(0, capacity, step=2))

    return fig