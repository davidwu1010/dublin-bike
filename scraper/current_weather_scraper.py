import requests
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, CurrentWeather, StaticBike
from config import MySQL, APIKeys


def scrape(craperDatetime):

    engine = create_engine(f'mysql+pymysql://{MySQL.username}:{MySQL.password}@{MySQL.host}/{MySQL.database}')
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    # fetch all stations info from database
    stations = session.query(StaticBike)

    if stations:
        for station in stations:

            url = f'http://api.openweathermap.org/data/2.5/weather?lat={station.latitude}&lon={station.longitude}&appid={APIKeys.openweather_key}&units=metric'
            # url = f'https://api.weatherbit.io/v2.0/current?lat={station.latitude}&lon={station.longitude}&key={APIKeys.weather_key}'
            response = requests.get(url)
            response.raise_for_status()

            if response:

                data = response.json()
                temp = data["main"]["temp"]
                # datetimeStr = data["datetime"]
                lon = data["coord"]["lon"]
                lat = data["coord"]["lat"]
                wind_spd = data["wind"]["speed"]
                clouds = data["clouds"]["all"]
                sunset = data["sys"]["sunset"]
                weather = data["weather"]
                icon = weather["icon"]
                code = weather["id"]
                description = weather["description"]

                datetimeObj = datetime.datetime.strptime(craperDatetime, '%Y-%m-%d:%H')
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





