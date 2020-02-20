import requests
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, CurrentWeather, StaticBike
from config import MySQL, APIKeys


def scrape():

    engine = create_engine(f'mysql+pymysql://{MySQL.username}:{MySQL.password}@{MySQL.host}/{MySQL.database}')
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    # fetch all stations info from database
    stations = session.query(StaticBike)

    if stations:
        for station in stations:

            url = f'https://api.weatherbit.io/v2.0/current?lat={station.latitude}&lon={station.longitude}&key={APIKeys.weather_key}'
            response = requests.get(url)
            response.raise_for_status()

            if response:

                data = response.json()['data'][0]
                temp = data["temp"]
                datetimeStr = data["datetime"]
                lon = data["lon"]
                lat = data["lat"]
                wind_spd = data["wind_spd"]
                clouds = data["clouds"]
                sunset = data["sunset"]
                weather = data["weather"]
                icon = weather["icon"]
                code = weather["code"]
                description = weather["description"]

                datetimeObj = datetime.datetime.strptime(datetimeStr, '%Y-%m-%d:%H')
                weekday = datetimeObj.isoweekday()

                # Only add new row to table of DB if the datetime(key) is not exist
                isDateTimeExist = session.query(exists().where(CurrentWeather.datetime == datetimeObj).where(CurrentWeather.stationNum == station.number)).scalar()

                if isDateTimeExist == False:
                    session.add(CurrentWeather(station.number, datetimeObj, lon, lat, temp, wind_spd, clouds, sunset, description, code, icon, weekday))
                    session.commit()

    else:
        print('Can not find stations')

if __name__ == '__main__':
    scrape()





