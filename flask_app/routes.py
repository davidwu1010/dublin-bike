import json

from flask import Flask, render_template, jsonify
from models.schemas import Forecast, CurrentWeather, DublinBike
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import config
from hourly_average import get_hourly_mean_json
from daily_average import get_daily_mean_json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.MySQL.URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/forecasts/<int:station_id>')
def get_forecasts(station_id):
    forecasts = db.session.query(Forecast) \
        .filter(Forecast.stationNum == station_id) \
        .order_by(Forecast.timestamp.asc( )).all( )
    return jsonify({
        'data': [forecast.serialize for forecast in forecasts]
    })


@app.route('/api/current-weather/<int:station_id>')
def get_current_weather(station_id):
    current_weather = db.session.query(CurrentWeather) \
        .filter(CurrentWeather.stationNum == station_id) \
        .order_by(CurrentWeather.datetime.desc( )).first( )
    return jsonify({
        'data': current_weather.serialize
    })


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
        .order_by(DublinBike.scraping_time.desc( )).first( )
    return jsonify({
        'data': station.serialize
    })


@app.route("/api/hourly/<int:station_id>")
def hourly_chart(station_id):
    data = get_hourly_mean_json(station_id)
    return data

@app.route("/api/daily/<int:station_id>")
def daily_chart(station_id):
    data = get_daily_mean_json(station_id)
    return data


if __name__ == '__main__':
    app.run()
