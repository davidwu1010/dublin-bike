from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, Boolean

Base = declarative_base()


class Forecast(Base):
    __tablename__ = 'forecasts'
    timestamp = Column(String(30), primary_key=True)
    temperature = Column(String(10))
    description = Column(String(30))
    icon = Column(String(30))


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
    banking = Column(Boolean())
    bonus = Column(Boolean)
