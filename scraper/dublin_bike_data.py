import requests
import datetime
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, DublinBike
from config import MySQL, APIKeys


def scrape():
    host = MySQL.host
    user = MySQL.username
    password = MySQL.password
    database = MySQL.database

    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    api = "https://api.jcdecaux.com/vls/v1/stations"
    parameters = {'contract': 'dublin', 'apiKey': APIKeys.bike_API}

    response = requests.get(api, verify=True, params=parameters)

    response.raise_for_status()  # throw an error if made a bad request

    if response:
        response = response.json()
        dt = datetime.now()
        for row in response:
            scraping_time = str(dt)
            number = row["number"]
            last_update = datetime.fromtimestamp(row["last_update"] / 1000)
            site_names = row["name"]
            address = row["address"]
            latitude = row["position"]['lat']
            longitude = row["position"]['lng']
            bike_stand = row["bike_stands"]
            available_bike_stand = row["available_bike_stands"]
            available_bike = row["available_bikes"]
            status = row["status"]
            banking = row["banking"]
            bonus = row["bonus"]
            session.add(DublinBike(scraping_time=scraping_time,
                                   number=number,
                                   last_update=last_update,
                                   site_names=site_names,
                                   address=address,
                                   latitude=latitude,
                                   longitude=longitude,
                                   bike_stand=bike_stand,
                                   available_bike_stand=available_bike_stand,
                                   available_bike=available_bike,
                                   status=status,
                                   banking=banking,
                                   bonus=bonus))

        session.commit()
        return dt


if __name__ == '__main__':
    scrape()
    ##???(dt)
