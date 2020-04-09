import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, Forecast, StaticBike
from config import MySQL, APIKeys
from datetime import datetime


# return weatherBit weather icon by given dark sky icon
def to_icon_code(description, is_night):
    icons = {'clear-day': 'c01', 'clear-night': 'c01', 'rain': 'r01',
             'snow': 's01', 'sleet': 's04', 'wind': 's05', 'fog': 'a05',
             'cloudy': 'c04', 'partly-cloudy-day': 'c02',
             'partly-cloudy-night': 'c02'}
    code = icons[description]
    if is_night:
        code += 'n'
    else:
        code += 'd'
    return code


def scrape():
    engine = create_engine(MySQL.URI)
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    # fetch all stations info from database
    stations = session.query(StaticBike)

    if stations:
        session.execute('TRUNCATE TABLE forecasts')  # clear the table

        for station in stations:

            parameters = {'exclude': 'minutely,flags', 'units': 'si'}
            lat = station.latitude
            lon = station.longitude
            api = f'https://api.darksky.net/forecast/' \
                  f'{APIKeys.darksky_key}/{lat},{lon}'

            response = requests.get(api, params=parameters)
            response.raise_for_status()  # throw an error if made a bad request
            if response:

                response = response.json()
                sunrise_time = response['daily']['data'][0]['sunriseTime']
                sunset_time = response['daily']['data'][0]['sunsetTime']
                for forecast in response['hourly']['data']:
                    is_night = forecast['time'] < sunrise_time \
                               or forecast['time'] > sunset_time
                    timestamp = datetime.fromtimestamp(forecast['time'])
                    temperature = forecast['temperature']
                    description = forecast['summary']
                    icon = to_icon_code(forecast['icon'], is_night)
                    session.add(Forecast(timestamp=timestamp,
                                         temperature=temperature,
                                         description=description,
                                         icon=icon,
                                         lat=station.latitude,
                                         lon=station.longitude,
                                         stationNum=station.number))
            session.commit()
    else:
        print('Can not find stations')


if __name__ == '__main__':
    scrape()
