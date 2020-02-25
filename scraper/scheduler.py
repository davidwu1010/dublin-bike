import logging
import signal
import sys
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from scraper import forecast_scraper, dublin_bike_data, current_weather_scraper


def signal_handler(sig, frame):
    scheduler.shutdown()
    sys.exit(0)


# scheduler will throw error if time zone not set
os.environ['TZ'] = 'Europe/Dublin'
sys.tracebacklimit = 0

signal.signal(signal.SIGINT, signal_handler)  # trap SIGINT (CTRL+C)
signal.signal(signal.SIGTERM, signal_handler)  # trap SIGTERM (kill)

logging.basicConfig(filename='scraper.log', filemode='a')
logging.getLogger("apscheduler").setLevel(logging.DEBUG)


def bike_weather_scraper():
    scraping_time = dublin_bike_data.scrape()
    current_weather_scraper.scrape(scraping_time)


scheduler = BlockingScheduler()
scheduler.add_job(forecast_scraper.scrape, 'interval', hours=1)
scheduler.add_job(bike_weather_scraper, 'interval', minutes=5)
scheduler.start()
