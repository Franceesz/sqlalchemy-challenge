# Import the dependencies.
import numpy as np
import flask
print(flask.__version__)
import sqlalchemy
print(sqlalchemy.__version__)
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from sqlalchemy import desc,asc
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session =Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Define a function which calculates and returns the the date one year from the most recent date
def last_year():
    session =Session(engine)
    # Define the most recent date in the Measurement dataset
    # Then use the most recent date to calculate the date one year from the last date
    latest_date=session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    year_ago= dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    # Close the session  
    session.close()
    # Return the date
    return(year_ago)
# Define what to do when the user hits the homepage
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )
@app.route("/api/v1.0/precipitation")
# Define what to do when the user hits the precipitation URL
def precipitation():
    # Create our session (link) from Python to the DB
    session =Session(engine)
    """Return a list of precipitation (prcp)and date (date) data"""
    precipitation_query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year()).order_by(asc(Measurement.date)).all()
    session.close()
    # Create a dictionary from the row data and append to a list of prcp_list
    result_todict=dict(precipitation_query_results)
    # Return a list of jsonified precipitation data for the previous 12 months
    return jsonify(result_todict)
# Define what to do when the user hits the station URL
@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    # Query station data from the Station dataset
    all_station = session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    station_list = list(np.ravel(all_station))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs") 
def tobs():
    session= Session(engine)
    # Query tobs data from last 12 months from the most recent date from Measurement table
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= last_year()).all()
    # Create a dictionary from the row data and append to a list of tobs_list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)

def valid_date(datestr):
    """Helper function to check if a date string is valid."""
    try:
        dt.datetime.strptime(datestr, "%Y-%m-%d")
    except ValueError:
        return False
    else :
        return True
@app.route("/api/v1.0/<start>")
def temp_info(start):
    session = Session(engine)
    # Check if there is an end date then do the task accordingly
    if valid_date(start) == False:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})
    else:
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        start_list = list(np.ravel(start_data))
        return jsonify(start_list)
        session.close()
       
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)
    if valid_date(start)== False or valid_date(end)==False:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."})
    else:
     # Query the data from start date to the end date
        start_toend_data= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        start_end_list=list(np.ravel(start_toend_data))
        return jsonify(start_end_list)
        session.close()
# Define main branch 
if __name__ == "__main__":
    app.run(debug = True)