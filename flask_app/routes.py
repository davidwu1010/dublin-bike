from flask import Flask, render_template, jsonify, request
from flask_app.bike_predict_next_hour import bike_predict_next_hour
from flask_app.houly_predict import bike_predict_hourly
from flask_app.daily_predict import bike_predict_daily
from models.schemas import Forecast, CurrentWeather, DublinBike
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import config
from flask_app.hourly_average import get_hourly_mean_json
from flask_app.daily_average import get_daily_mean_json
from datetime import datetime

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
        .filter(Forecast.stationNum == station_id,
                Forecast.timestamp > datetime.utcnow()) \
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


@app.route("/api/hourly/<int:station_id>")
def hourly_chart(station_id):
    data = get_hourly_mean_json(station_id)
    return data


@app.route("/api/daily/<int:station_id>")
def daily_chart(station_id):
    data = get_daily_mean_json(station_id)
    return data


@app.route('/api/prediction/<int:station_id>')
def get_prediction(station_id):
    day = request.args.get('day')
    time = request.args.get('time')
    return str(day) + str(time)


@app.route('/api/get_prediction_hourly/<int:station_id>')
def get_prediction_hourly_chart(station_id):
    data = bike_predict_hourly(station_id)
    return data


@app.route('/api/get_prediction_daily/<int:station_id>')
def get_prediction_daily_chart(station_id):
    data = bike_predict_daily(station_id)
    return data


@app.route('/api/get_prediction_next_hour/<int:station_id>')
def get_prediction_next_hour(station_id):
    data = bike_predict_next_hour(station_id)
    return data


if __name__ == '__main__':
    app.run()
