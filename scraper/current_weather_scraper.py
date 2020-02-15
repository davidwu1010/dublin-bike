import requests
import sys
from flask_app.routes import db
from scraper.models import Current_weather

def scrape():

    city = "dublin,ie"
    key = "e1e57d828ca04314a28b8bb9e9ad0a90"
    url = "https://api.weatherbit.io/v2.0/current?city={}&key={}".format(city, key)

    try:
        req = requests.get(url)
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

    data = req.json()[0]
    temp = data["temp"]
    datetime = data["datetime"]
    weather = data["weather"]
    icon = weather["icon"]
    description = weather["description"]

    cur_weather_data = Current_weather(datetime, temp, description, icon)

    try:
        db.session.add(cur_weather_data)
        db.session.commit()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

scrape()
