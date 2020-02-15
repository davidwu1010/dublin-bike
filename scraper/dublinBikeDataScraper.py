from typing import List

import requests
import datetime
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine


def get_df(dataDict):
    dt = str(datetime.now())
    for i in dataDict:
        number = [i["number"] for i in dataDict]
        time = [datetime.fromtimestamp(i["last_update"] / 1000) for i in dataDict]
        site_names = [i["name"] for i in dataDict]
        address = [i["address"] for i in dataDict]
        lat = [i["position"]['lat'] for i in dataDict]
        lng = [i["position"]['lng'] for i in dataDict]
        bike_stand = [i["bike_stands"] for i in dataDict]
        avl_bike_stand = [i["available_bike_stands"] for i in dataDict]
        avl_bike = [i["available_bikes"] for i in dataDict]
        status = [i["status"] for i in dataDict]
        banking = [i["banking"] for i in dataDict]
        bonus = [i["bonus"] for i in dataDict]
    scraping_time = [str(dt) for i in range(len(dataDict))]

    bike_dict = {
        "Number": number,
        "Time": time,
        "Address": address,
        "Site Names": site_names,
        "Latitude": lat,
        "Longitude": lng,
        "Bike Stand": bike_stand,
        "Available BikeStank": avl_bike_stand,
        "Available Bike": avl_bike,
        "Status": status,
        "Banking": banking,
        "Bonus": bonus,
        "Scraping Time": scraping_time
    }

    df = pd.DataFrame(bike_dict)
    return df


def scrape():
    r = requests.get(
        "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=7ae2177f685f108ca05b6adce96561f8cf959aa5",
        verify=True)
    if r.status_code == 200:
        dataDict = r.json()
        dfBike = get_df(dataDict)
        # dt = str(datetime.now())
        # fileName = 'bike_' + dt + '.csv'
        # dfBike.to_csv(fileName, index=False)

        host = 'database-1.cmv75f0i1uzy.eu-west-1.rds.amazonaws.com'
        engine = create_engine(f"mysql+pymysql://dev:qwerty@{host}/development")

        connection = engine.connect()

        dfBike.to_sql(name='dublinBike', con=engine, if_exists='append', index=False)
    elif r.status_code == 301:
        print('Server redirect to another address!')
    elif r.status_code == 400:
        print('Error request!')
    elif r.status_code == 401:
        print('Server redirect to another address!')
    elif r.status_code == 403:
        print('License error!')
    elif r.status_code == 404:
        print('Fail request!')

scrape()
