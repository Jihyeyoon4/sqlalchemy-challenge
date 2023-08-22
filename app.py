# Import the dependencies.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

import numpy as np
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import desc

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Measurement=Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

#################################################
# Flask Routes
#################################################

# a function to get latest date in measurement table
def get_most_recent_date():
    most_recent_row = session.query(Measurement).order_by(desc(Measurement.date)).first()
    most_recent_date = dt.datetime.strptime(most_recent_row.date, "%Y-%m-%d")
    return most_recent_date

# a function to calculate the date represent 12 month ago of any given date
def get_one_year_ago(date):
    one_year_delta = dt.timedelta(days=365)
    starting_date = date - one_year_delta
    return starting_date

# a route to get precipitation data for the past 12 months
@app.route("/api/v1.0/precipitation")
def prcp():
    most_recent_date = get_most_recent_date()
    starting_date = get_one_year_ago(most_recent_date)
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= starting_date)
    response = {}
    for row in results:
        response[row[0]] = row[1]

    return jsonify(response)

# a route to get all stations and return station code and station name
@app.route("/api/v1.0/stations")
def station():
    results = session.query(Station.station, Station.name)
    response = []
    for row in results:
        response.append({
            "station": row[0],
            "name": row[1] 
        })
    return jsonify(response)

# a route to get all tobs data points of the most active station
@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = get_most_recent_date()
    starting_date = get_one_year_ago(most_recent_date)

    result = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station).order_by(desc(func.count(Measurement.station))).first()
    most_active_station = result[0]

    results = session.query(Measurement.tobs).filter(Measurement.date>=starting_date).filter(Measurement.station==most_active_station)

    response = []
    for row in results:
        response.append(row[0])
    return jsonify(response)

# a route to calculate min, avg, max of all the data points with date greater and equal to given start date
@app.route("/api/v1.0/<start>")
def temp_start_only(start):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).first()
    response = {
        "TMIN": result[0],
        "TAVG": result[1],
        "TMAX": result[2],
    }
    return jsonify(response)

# a route to calculate min, avg, max of all the data points with date is greater and equal to given start date, and date is less and equal to given start date
@app.route("/api/v1.0/<start>/<end>")
def temp_start_end(start, end):
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).first()
    response = {
        "TMIN": result[0],
        "TAVG": result[1],
        "TMAX": result[2],
    }
    return jsonify(response)