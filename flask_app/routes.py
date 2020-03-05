from flask import Flask, render_template, jsonify
from models.schemas import Forecast, CurrentWeather, DublinBike, StaticBike
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.MySQL.URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/station')
def station():
    return render_template('station.html')


@app.route('/api/forecasts/<int:station_id>')
def get_forecasts(station_id):
    forecasts = db.session.query(Forecast) \
        .filter(Forecast.stationNum == station_id) \
        .order_by(Forecast.timestamp.asc()).all()
    return jsonify({
        'data': [forecast.serialize for forecast in forecasts]
    })


@app.route('/api/current-weather/<int:station_id>')
def get_current_weather(station_id):
    current_weather = db.session.query(CurrentWeather) \
        .filter(CurrentWeather.stationNum == station_id) \
        .order_by(CurrentWeather.datetime.desc()).first()
    return jsonify({
        'data': current_weather.serialize
    })


@app.route('/api/stations/')
def get_static_stations():
    static_stations = db.session.query(StaticBike).all()
    return jsonify({
        'data': [station.serialize for station in static_stations]
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
