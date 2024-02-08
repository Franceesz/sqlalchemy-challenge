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
def last_year():
    session =Session(engine)
    """Return a list of precipitation (prcp)and date (date) data"""
    latest_date=session.query(Measurement.date).order_by(desc(Measurement.date)).first()
    year_ago= dt.datetime.strptime(latest_date[0], "%Y-%m-%d") - dt.timedelta(days=365)
    
    session.close()
    return(year_ago)
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
def precipitation():
    # Create our session (link) from Python to the DB
    session =Session(engine)
    """Return a list of precipitation (prcp)and date (date) data"""
    precipitation_query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_year()).order_by(asc(Measurement.date)).all()
    session.close()

    date_precipitation_list_dic = []
    for prcp, date in precipitation_query_results:
        date_precipitation_dic = {}
        date_precipitation_dic["precipitation"] = prcp
        date_precipitation_dic["date"] = date
        date_precipitation_list_dic.append(date_precipitation_dic)
    return jsonify(date_precipitation_list_dic)

@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
    all_station = session.query(Station.station).all()
    session.close()
    # Convert list of tuples into normal list
    station_list = list(np.ravel(all_station))
    return jsonify(station_list)

@app.route("/api/v1.0/tobs") 
def tobs():
    session= Session(engine)
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
                        filter(Measurement.date >= last_year()).all()
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        tobs_list.append(tobs_dict)

    # Return a list of jsonified tobs data for the previous 12 months
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temp_info(start=None,end=None):
    session = Session(engine)
    if end == None:
        start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        start_list = list(np.ravel(start_data))
        return jsonify(start_list)
    else:
        start_toend_data= session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        start_end_list=list(np.ravel(start_toend_data))
        return jsonify(start_end_list)
    session.close()
if __name__ == "__main__":
    app.run(debug = True)