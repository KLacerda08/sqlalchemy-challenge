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

# Perform a query to retrieve the data and precipitation scores
#note that func.avg ignores null values so that they are not factored into the average.  

last_year = session.query(measurement.date, func.avg(measurement.prcp)).\
    filter(measurement.date > start_date).\
    group_by(measurement.date).all() 

# Save the query results as a Pandas DataFrame and set the index to the date column
prcp_df = pd.DataFrame(last_year, columns = ['Date', 'Precip (in)'])
prcp_df.set_index('Date',inplace=True)
prcp_df['Precip (in)'] = prcp_df['Precip (in)'].round(2)

# Sort the dataframe by date (although it already looks to be sorted by date)
prcp_df = prcp_df.sort_index(ascending=True)

##----------------------------------------------------------------------------------
## FLASK QUESTIONS ##
#Get start and end dates for most frequently observed station
latest_date2 = session.query(measurement.date).\
        filter(measurement.station == 'USC00519281').\
        order_by(measurement.date.desc()).first()

start_date2 = dt.date(2017, 8, 18) - dt.timedelta(days=365)

prcp_dict = prcp_df.to_dict()

sta_list = session.query(station.station).order_by(station.station).all()

top_sta = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).first()

tobs2 = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519281').\
        filter(measurement.date > start_date2).all()

# Convert to dictionary
tobs2_df = pd.DataFrame(tobs2, columns = ["Date", 'tobs'])
tobs2_df.set_index('Date',inplace=True)
tobs2_df = tobs2_df.sort_index(ascending=True)
tobs2_dict = tobs2_df.to_dict()
##----------------------------------------------------------------------------------
##----------------------------------------------------------------------------------

## create app
app = Flask(__name__)

## Define routes
@app.route('/')
def home():
    print("Someone is accessing the homepage")
    return(
        f"<h1>Welcome to our Weather Data Homepage!</h1>"
        f"<h2>Available Routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs_top_station_id<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD<br/>"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"/about")


@app.route('/api/v1.0/precipitation')
def precipitation():
    # Using the query from part 1 (most recent 12 months of precipitation data), convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary (note the specific format of your dictionary as required from above).
    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
    #Get Station List
    #Return a JSON list of stations from the dataset.
    return jsonify(sta_list)

@app.route('/api/v1.0/tobs_top_station_id')
def tobs_top_station_id():
    # Added this page to list the "top station" so that the tobs data can make a little sense.  
    return (
        f'<h3>The most frequently measured weather station from {start_date2} to {latest_date2} was:<h3>'
        f'&nbsp &nbsp {top_sta}')

@app.route('/api/v1.0/tobs')
def tobs():
        # Query the dates and temperature observations of the most active station for the latest year of data.
        # Return a JSON list of temperature observations (TOBS) for that year.
    return jsonify(tobs2_dict)
        
@app.route('/api/v1.0/<start>')
def search_by_start_date(start):
    session = Session(engine)
    # start = input("Input start date (YYYY-MM-DD):  ")
    sel = [func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)]        

    query_search = session.query(*sel).filter(measurement.date >= start).all()
    results = list(np.ravel(query_search))

    ##could put min max ave in dict and return jsonify(dict)
    session.close()

    return jsonify(results)

@app.route('/api/v1.0/<start>/<end>')
def search_by_date_range(start, end):
    session = Session(engine)
    # start = input("Input start date (YYYY-MM-DD):  ")
    sel = [func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)]        
   
    # query_search = session.query(*sel).where(between(measurement.date, start, end).all()
    query_search = session.query(*sel).filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    results = list(np.ravel(query_search))

    ##could put min max ave in dict and return jsonify(dict)
    session.close()

    return jsonify(results)


#for start end, use a func.between (-check sql for syntax) or add new .filter(measurement.date
# # <end).all() 

#/api/v1.0/<start>/<end>
    # Create a query that returns the minimum temperature, the average temperature, and the max temperature for 
    # a given start or start-end range.
    #     Hint: You will need to use a function such as func.min, func.max, func.avg, and func.count in your queries.
    # When given the start date only, calculate min, max, and avg for all dates greater than and equal to the start date.
    # When given the start and the end date, calculate the min, avg, and max for dates between the start and end date inclusive.
    # Return a JSONified dictionary of min, max, and avg temperatures.


@app.route("/about")
def about(): 
    return f"We evaluate temperature data for Hawaii."


if __name__ == "__main__":
    app.run(debug=True)
