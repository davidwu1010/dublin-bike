from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float, DateTime, Integer, Boolean
from sqlalchemy import Column, String, Integer, Float, Boolean

Base = declarative_base()


class Forecast(Base):
    __tablename__ = 'forecasts'
    timestamp = Column(String(30), primary_key=True)
    temperature = Column(String(10))
    description = Column(String(30))
    icon = Column(String(30))


class Current_weather(Base):
    __tablename__ = 'current_weather'
    datetime = Column(DateTime(30), primary_key=True, nullable=False)
    temperature = Column(String(30), nullable=False)
    description = Column(String(30))
    icon = Column(String(30))
    lon = Column(Float(30))
    lat = Column(Float(30))
    wind_spd = Column(Float(30))
    clouds = Column(Float(30))
    sunset = Column(String(30))
    code = Column(String(30))
    weekday = Column(Integer())

    def __init__(self, datetime, lon, lat, temperature, wind_spd, clouds, sunset, description, code, icon, weekday):
        self.datetime = datetime
        self.lon = lon
        self.lat = lat
        self.temperature = temperature
        self.wind_spd = wind_spd
        self.clouds = clouds
        self.sunset = sunset
        self.description = description
        self.code = code
        self.icon = icon
        self.weekday = weekday

class DublinBike(Base):
    __tablename__ = 'dublin_bike'
    scraping_time = Column(String(32), primary_key=True)
    number = Column(Integer, primary_key=True)
    last_update = Column(String(32))
    address = Column(String(64))
    site_names = Column(String(64))
    latitude = Column(Float)
    longitude = Column(Float)
    bike_stand = Column(Integer)
    available_bike_stand = Column(Integer)
    available_bike = Column(Integer)
    status = Column(String(16))
    banking = Column(Boolean)
    bonus = Column(Boolean)
