import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, Forecast


def scrape():
    host = 'database-1.cmv75f0i1uzy.eu-west-1.rds.amazonaws.com'
    engine = create_engine(f'mysql+pymysql://dev:qwerty@{host}/development')
    Base.metadata.create_all(engine)  # Create table
    Session = sessionmaker(bind=engine)
    session = Session()

    parameters = {'city': 'Dublin', 'country': 'IE', 'hours': '6',
                  'key': '9045a4958d8f45e1a54f6607ff2ed1d2'}
    api = 'https://api.weatherbit.io/v2.0/forecast/hourly'

    response = requests.get(api, params=parameters)
    response.raise_for_status()  # throw an error if made a bad request
    if response:
        session.execute('TRUNCATE TABLE forecasts')  # clear the table
        response = response.json()
        for forecast in response['data']:
            timestamp = forecast['timestamp_local']
            temperature = forecast['temp']
            description = forecast['weather']['description']
            icon = forecast['weather']['icon']
            session.add(Forecast(timestamp=timestamp, temperature=temperature,
                                 description=description, icon=icon))
        session.commit()


if __name__ == '__main__':
    scrape()
