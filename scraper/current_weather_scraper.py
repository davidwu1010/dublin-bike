import requests
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, CurrentWeather, StaticBike
from config import MySQL, APIKeys

def to_weatherbit_icon(openweatherIcon):
    icons = {'11': 't04', '09': 'd01', '10': 'r01', '13': 'f01', '09': 'r04',
             '13': 's02', '50': 'a02', '01': 'c01',  '02': 'c02', '03': 'c03',
             '04': 'c04'}
    return icons[openweatherIcon[:-1]]+openweatherIcon[-1]


def scrape(dt):

    engine = create_engine(f'mysql+pymysql://{MySQL.username}:{MySQL.password}@{MySQL.host}/{MySQL.database}')
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    # fetch all stations info from database
    stations = session.query(StaticBike)

    if stations:
        for station in stations:

            url = f'http://api.openweathermap.org/data/2.5/weather?lat={station.latitude}&lon={station.longitude}&appid={APIKeys.openweather_key}&units=metric'
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
                print("weather icon", weather["icon"], "icon", icon)
                code = weather["id"]
                description = weather["description"]

                datetimeObj = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
                weekday = datetimeObj.isoweekday()

                # Only add new row to table of DB if the datetime(key) is not exist
                isDateTimeExist = session.query(exists().where(CurrentWeather.datetime == datetimeObj).where(CurrentWeather.stationNum == station.number)).scalar()

                if isDateTimeExist == False:
                    session.add(CurrentWeather(station.number, datetimeObj, lon, lat, temp, wind_spd, clouds, sunset, description, code, icon, weekday))
                    session.commit()

    else:
        print('Can not find stations')

