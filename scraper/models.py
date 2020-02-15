from flask_app.routes import db

class Current_weather(db.Model):
    __tablename__ = 'current_weather'
    datetime = db.Column(db.String(30), primary_key=True, nullable=False)
    temperature = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(30))
    icon = db.Column(db.String(30))

    def __init__(self, datetime, temperature, description, icon):
        self.datetime = datetime
        self.temperature = temperature
        self.description = description
        self.icon = icon