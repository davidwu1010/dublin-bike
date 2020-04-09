import sys
sys.path.insert(0, '/home/ubuntu/dublin_bikes')

from routes import app

if __name__ == '__main__':
    app.run()
