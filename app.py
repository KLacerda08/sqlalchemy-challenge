## Import Dependencies
from flask import Flask, jsonify

## %matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

import datetime as dt

## Access data from sqlite

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


## Queries and data 
latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()

start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
print(start_date)

# ## create app
# app = Flask(__name__)

# ## Define routes
# @app.route('/')
# def home():
#     print("Someone is accessing the homepage")
#     return(
#         f"<h1>Welcome to our homepage!</h1>"
#         f"<h2>Available Routes:</h2>"
#         f"/api/v1.0/precipitation<br/>"
#         f"/api/v1.0/stations<br/>"
#         f"/api/v1.0/tobs<br/>"
#         f"/api/v1.0/start<br/>"
#         f"/api/v1.0/start_end<br/>"
#         f"/about")


# # @app.route('/api/v1.0/precipitation')

#     # Using the query from part 1 (most recent 12 months of precipitation data), convert the query results to a dictionary using date as the key and prcp as the value.
#     # Return the JSON representation of your dictionary (note the specific format of your dictionary as required from above).



# # @app.route('/api/v1.0/stations')

# # @app.route('/api/v1.0/tobs')

# # @app.route('/api/v1.0/<start>')

# # @app.route('/api/v1.0/<start>/<end>')


# @app.route("/about")
# def about():
       
#     return f"We evaluate temperature data for Hawaii."


# if __name__ == "__main__":
#     app.run(debug=True)
