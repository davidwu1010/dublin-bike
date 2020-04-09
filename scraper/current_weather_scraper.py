import requests
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, CurrentWeather, StaticBike
from config import MySQL, APIKeys


# return weatherBit weather condition icon by given open weather icon
def to_weatherbit_icon(openweatherIcon):

    # Key: open weather icon; value: weather bit icon
    icons = {'11': 't04', '09': 'd01', '10': 'r01', '13': 'f01', '50': 'a02',
             '01': 'c01',  '02': 'c02', '03': 'c03', '04': 'c04'}

    return icons[openweatherIcon[:-1]] + openweatherIcon[-1]


def scrape(dt):

    engine = create_engine(MySQL.URI)
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    # fetch all stations data from database
    stations = session.query(StaticBike)

    if stations:
        for station in stations:

            url = f'http://api.openweathermap.org/data/2.5/weather?' \
                  f'lat={station.latitude}' \
                  f'&lon={station.longitude}' \
                  f'&appid={APIKeys.openweather_key}' \
                  f'&units=metric'

            response = requests.get(url)
            response.raise_for_status()

            if response:

                data = response.json()
                temp = data["main"]["temp"]
                lon = data["coord"]["lon"]
                lat = data["coord"]["lat"]
                wind_spd = data["wind"]["speed"]
                clouds = data["clouds"]["all"]
                sunset = data["sys"]["sunset"]
                weather = data["weather"][0]
                icon = to_weatherbit_icon(weather["icon"])
                code = weather["id"]
                description = weather["description"]

                dtObj = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                weekday = dtObj.isoweekday()

                isDateTimeExist = session\
                    .query(exists()
                           .where(CurrentWeather.datetime
                                  == dtObj)
                           .where(CurrentWeather.stationNum
                                  == station.number))\
                    .scalar()

                # Only add to DB if the datetime(key) is not exist
                if not isDateTimeExist:
                    session.add(CurrentWeather(station.number, dtObj,
                                               lon, lat, temp, wind_spd,
                                               clouds, sunset, description,
                                               code, icon, weekday))
                    session.commit()

    else:
        print('Can not find stations')
