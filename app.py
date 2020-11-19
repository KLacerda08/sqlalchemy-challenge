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

##----------------------------------------------------------------------------------
## FLASK APP  ##

## create app
app = Flask(__name__)

## Define routes
@app.route('/')
def home():

    print("Someone is accessing the homepage")
    return(
        f"<h1>Welcome to our Weather Data Homepage!</h1>"
        f"<h2>Available Routes:</h2>"
        f"About Us: <br/>/about<br/><br/>"
        f"Precipitation Data - Most Recent 12 Months:  <br/>/api/v1.0/precipitation<br/><br/>"
        f"Station List:  <br/>/api/v1.0/stations<br/><br/>"
        f"Most Frequently Measured Station (in Last 12 Months): <br/>/api/v1.0/id_top_station<br/><br/>"
        f"Temperature Data from Most Frequently Measured Station: <br/>/api/v1.0/tobs_top_station<br/><br/>"
        f"Temperature Stats by Start Date (YYYY-MM-DD): <br/>/api/v1.0/start<br/><br/>"
        f"Temperature Stats by Date Range (YYYY-MM-DD): <br/>/api/v1.0/start/end")

@app.route("/about")
def about(): 
    return (
            f"<h2>About Us:  We provide weather data for Hawaii!</h2>"
            f" The database includes temperature and precipitation monitoring of several weather stations \
                throughout Hawaii from January 1, 2010 through August 23, 2017.<br/>\
                To search temperature data by date, use date format: YYYY-MM-DD.<br/>\
                The most frequently measured station ID can be found at the following route:\
                /api/v1.0/id_top_station")

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)

    # Using the query from part 1 (most recent 12 months of precipitation data), 
    # convert the query results to a dictionary using date as the key and prcp as the value.
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    last_year = session.query(measurement.date, func.avg(measurement.prcp)).\
        filter(measurement.date > start_date).\
        group_by(measurement.date).all() 

    # Save the query results as a DataFrame, set the index to the date column, round precip values
    prcp_df = pd.DataFrame(last_year, columns = ['Date', 'Precip (in)'])
    prcp_df.set_index('Date',inplace=True)
    prcp_df['Precip (in)'] = prcp_df['Precip (in)'].round(2)
    
    # Sort the dataframe by date and put into dictionary
    prcp_df = prcp_df.sort_index(ascending=True)
    prcp_dict = prcp_df.to_dict()
    
    session.close()
    return jsonify(prcp_dict)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)

    #Get Station List
    sta_list = session.query(station.station).order_by(station.station).all()
    
    session.close()
    return jsonify(sta_list)

@app.route('/api/v1.0/id_top_station')
def id_top_station():
    # Added this page to identify the "top station" (most active station) for the latest year of data.  
    session = Session(engine)
   
    # Get start and end dates of most recent 12 months of data  
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the latest year of data.
    top_sta = session.query(measurement.station).\
        group_by(measurement.station).\
        filter(measurement.date > start_date).\
        order_by(func.count(measurement.station).desc()).first()

    session.close()
    return (
        f'<h3>The most frequently measured weather station for the most recent year of data ({start_date} to \
            {latest_date}) was:</h3> &nbsp &nbsp {top_sta}'
            )

@app.route('/api/v1.0/tobs_top_station')
def tobs():
    session = Session(engine) 

    # Get start and end dates of most recent 12 months of data  
    latest_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    start_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #Get tobs from the station identified in the prior page(USC00519397)
    tobs2 = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == 'USC00519397').\
        filter(measurement.date > start_date).all()
    
    # Convert to dictionary
    tobs2_df = pd.DataFrame(tobs2, columns = ["Date", 'tobs'])
    tobs2_df.set_index('Date',inplace=True)
    tobs2_df = tobs2_df.sort_index(ascending=True)
    tobs2_dict = tobs2_df.to_dict()
    
    session.close()
    return jsonify(tobs2_dict)

@app.route('/api/v1.0/<start>')
def search_by_start_date(start):
    session = Session(engine)
    
    #calculate min, max, and avg for all dates greater than and equal to the queried start date.  

    sel = [func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)]

    startdate_stats = session.query(*sel).filter(measurement.date >= start).all()

    tobs_start = pd.DataFrame(startdate_stats, columns = ["Min Temp", 'Max Temp', "Avg Temp"])
    tobs_start = tobs_start.to_dict()

    session.close()
    return jsonify(tobs_start)

@app.route('/api/v1.0/<start>/<end>')
def search_by_date_range(start, end):
    session = Session(engine)

    #calculate min, max, and avg for all dates between the queried start and end dates:

    sel = [func.min(measurement.tobs),
        func.max(measurement.tobs),
        func.avg(measurement.tobs)]        
   
    date_range_stats = session.query(*sel).filter(measurement.date >= start).\
        filter(measurement.date <= end).all()

    tobs_date_range = pd.DataFrame(date_range_stats, columns = ["Min Temp", 'Max Temp', "Avg Temp"])
    tobs_date_range = tobs_date_range.to_dict()

    session.close()
    return jsonify(tobs_date_range)

if __name__ == "__main__":
    app.run(debug=True)
