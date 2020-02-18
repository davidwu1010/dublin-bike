from flask import Flask, render_template, jsonify
from models.schemas import Forecast, Current_weather
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.MySQL.username}:{config.MySQL.password}@{config.MySQL.host}/{config.MySQL.database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/forecasts/')
def get_forecast():
    forecasts = db.session.query(Forecast).all()
    return jsonify({
        'data': [forecast.serialize for forecast in forecasts]
    })


@app.route('/api/current-weather/')
def get_current_weather():
    current_weather = db.session.query(Current_weather).\
        order_by(Current_weather.datetime.desc()).first()
    return jsonify({
        'data': current_weather.serialize
    })


@app.route('/api/stations/')
def get_all_stations():
    return '1'


@app.route('/api/stations/<int:id>')
def get_station(station_id):
    return '1'


if __name__ == '__main__':
    app.run()
