class MySQL:
    host = 'database-1.cmv75f0i1uzy.eu-west-1.rds.amazonaws.com'
    username = 'dev'
    password = 'qwerty'
    database = 'development'
    URI = f'mysql+pymysql://{username}:{password}@{host}/{database}'


class APIKeys:
    forecast_key = '9045a4958d8f45e1a54f6607ff2ed1d2'
    weather_key = 'e1e57d828ca04314a28b8bb9e9ad0a90'
    openweather_key = '66043352f756672c33e75e84356d00bb'
    bike_API = '7ae2177f685f108ca05b6adce96561f8cf959aa5'
