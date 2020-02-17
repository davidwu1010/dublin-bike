from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()


class Forecast(Base):
    __tablename__ = 'forecasts'
    timestamp = Column(String(30), primary_key=True)
    temperature = Column(String(10))
    description = Column(String(30))
    icon = Column(String(30))