import csv
from time import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.schemas import Base, StaticBike
from config import MySQL

#Build static bike station id table
if __name__ == "__main__":
    t = time()
    engine = create_engine(MySQL.URI)
    Base.metadata.create_all(engine)

    session = sessionmaker()
    session.configure(bind=engine)
    s = session()

    file_name = "dublin.csv"

    try:
        with open(file_name) as csvfile:
            data = csv.reader(csvfile)
            next(data, None)
            for row in data:
                record = StaticBike(**{
                    'number': row[0],
                    'name': row[1],
                    'address': row[2],
                    'latitude': row[3],
                    'longitude': row[4]
                })
                s.add(record)
            s.commit()

    except:
        s.rollback()  # Rollback the changes on error
    finally:
        s.close()  # Close the connection
    print("Time elapsed: " + str(time() - t) + " s.")
