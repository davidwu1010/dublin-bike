from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

host = "database-1.cmv75f0i1uzy.eu-west-1.rds.amazonaws.com"
user = "dev"
password = "qwerty"
dbname = "development"

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{password}@{host}/{dbname}'
db = SQLAlchemy(app)



@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
