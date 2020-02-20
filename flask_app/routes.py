from flask import Flask, render_template, jsonify
from models.schemas import Forecast, CurrentWeather, DublinBike
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.MySQL.username}:{config.MySQL.password}@{config.MySQL.host}/{config.MySQL.database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/forecast/')
def get_forecast():
    forecasts = db.session.query(Forecast).all()
    return jsonify({
        'data': [forecast.serialize for forecast in forecasts]
    })


@app.route('/api/current-weather/')
def get_current_weather():
    current_weather = db.session.query(CurrentWeather). \
        order_by(CurrentWeather.datetime.desc()).first()
    return jsonify({
        'data': current_weather.serialize
    })


@app.route('/api/stations/')
def get_all_stations():
    stations_list = []
    all_stations = db.session.query(DublinBike.number, DublinBike.site_names, DublinBike.latitude,
                                    DublinBike.longitude).distinct().all()
    for station in all_stations:
        station_dict = {'number': station.number, 'site_names': station.site_names, 'latitude': station.latitude,
                        'longitude': station.longitude}
        stations_list.append(station_dict)
    return jsonify({
        'data': stations_list
    })


@app.route('/api/stations/<int:id>')
def get_station(station_id):
    station = db.session.query(DublinBike).filter(DublinBike.number == station_id). \
        order_by(DublinBike.scraping_time.desc()).first()
    return jsonify({
        'data': station.serialize
    })


if __name__ == '__main__':
    app.run()
