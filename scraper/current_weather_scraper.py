from flask_sqlalchemy import SQLAlchemy
import requests
import sys
import flask_app.routes

host = "database-1.cmv75f0i1uzy.eu-west-1.rds.amazonaws.com"
user = "dev"
password = "qwerty"
dbname = "development"

flask_app.routes.app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{dbname}'
db = SQLAlchemy(flask_app.routes.app)

class Current_weather(db.Model):
    __tablename__ = 'current_weather'
    datetime = db.Column(db.String(30), primary_key=True, nullable=False)
    temperature = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(30))
    icon = db.Column(db.String(30))

    def __init__(self, datetime, temperature, description, icon):
        self.datetime = datetime
        self.temperature = temperature
        self.description = description
        self.icon = icon

def scrape():

    city = "dublin,ie"
    key = "e1e57d828ca04314a28b8bb9e9ad0a90"
    url = "https://api.weatherbit.io/v2.0/current?city={}&key={}".format(city, key)

    try:
        req = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    json = req.json()
    data = json["data"][0]
    temp = data["temp"]
    datetime = data["datetime"]
    weather = data["weather"]
    icon = weather["icon"]
    description = weather["description"]

    cur_weather_data = Current_weather(datetime, temp, description,icon )
    try:
        db.session.add(cur_weather_data)
        db.session.commit()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


scrape()
