from flask import Flask, render_template
from models.schemas import Forecast
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{config.MySQL.username}:{config.MySQL.password}@{config.MySQL.host}/{config.MySQL.database}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/forecast/')
def get_forecast():
    return '0'


@app.route('/api/current-weather/')
def get_current_weather():
    return '1'


@app.route('/api/stations/')
def get_all_stations():
    return '1'


@app.route('/api/stations/<int:id>')
def get_station(station_id):
    return '1'


if __name__ == '__main__':
    app.run()
