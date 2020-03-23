from flask import Flask, render_template, jsonify
from models.schemas import Forecast, CurrentWeather, DublinBike, StaticBike
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.MySQL.URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/weather/<int:station_id>')
def get_weather(station_id):

    # get forcast weather data from db
    forecasts = db.session.query(Forecast) \
        .filter(Forecast.stationNum == station_id) \
        .order_by(Forecast.timestamp.asc()).all()

    # get current weather data from db
    current_weather = db.session.query(CurrentWeather) \
        .filter(CurrentWeather.stationNum == station_id) \
        .order_by(CurrentWeather.datetime.desc()).first()

    data = {'current': current_weather.serialize,
            'forecast': [forecast.serialize for forecast in forecasts]}
    return jsonify(data)


@app.route('/api/stations/')
def get_all_stations():
    latest_scraping_time = db.session \
        .query(func.max(DublinBike.scraping_time)).one()[0]
    stations = db.session.query(DublinBike) \
        .filter(DublinBike.scraping_time == latest_scraping_time) \
        .order_by(DublinBike.number.asc()).all()
    return jsonify({
        'data': [station.serialize for station in stations]
    })


@app.route('/api/stations/<int:station_id>')
def get_station(station_id):
    station = db.session.query(DublinBike) \
        .filter(DublinBike.number == station_id) \
        .order_by(DublinBike.scraping_time.desc()).first()
    return jsonify({
        'data': station.serialize
    })


if __name__ == '__main__':
    app.run()
