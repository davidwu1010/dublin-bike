import requests
import datetime
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, Current_weather
from config import MySQL, APIKeys
import logging


def scrape():

    city = "dublin,ie"
    url = f'https://api.weatherbit.io/v2.0/current?city={city}&key={APIKeys.weather_key}'

    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(e)

    data = res.json()['data'][0]
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

    try:
        engine = create_engine(f'mysql+pymysql://{MySQL.username}:{MySQL.password}@{MySQL.host}/{MySQL.database}')
        Base.metadata.create_all(engine)  # Create table
        Session = sessionmaker(bind=engine)
        session = Session()

        # Only add new row to table of DB if the datetime(key) is not exist
        isDateTimeExist = session.query(exists().where(Current_weather.datetime == datetimeObj)).scalar()
        if isDateTimeExist == False:

            session.add(Current_weather(datetimeObj, lon, lat, temp, wind_spd, clouds, sunset, description, code, icon, weekday))
            session.commit()

    except Exception as e:
        logging.error(e)

logging.basicConfig(filename='currentWeatherScraper.log',level=logging.DEBUG)
scrape()




