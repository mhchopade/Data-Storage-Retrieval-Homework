import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        "/api/v1.0/&lt;start&gt;<br/>"
        "/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all dates with precipitation"""
    # Query all measurements
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Convert the query results to a Dictionary using date as the key and prcp as the value.
    # Create a dictionary from the row data and append to a list of all_measurements
    all_measurements = []
    for measurement in results:
        measurement_dict = {}
        measurement_dict[measurement.date] = measurement.prcp
        all_measurements.append(measurement_dict)

    # Return the JSON representation of your dictionary.
    return jsonify(all_measurements)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    # Query all stations
    results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return a JSON list of stations from the dataset.
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all dates with temperature observations starting one year prior to last date"""
    # Query for the dates and temperature observations from a year from the last data point.
    # Query all measurements
    results = session.query(Measurement).filter(Measurement.date >= '2016-08-23').all()

    # Create a dictionary from the row data and append to a list of all_measurements
    all_measurements = []
    for measurement in results:
        measurement_dict = {}
        measurement_dict[measurement.date] = measurement.tobs
        all_measurements.append(measurement_dict)

    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(all_measurements)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps(start, end='2017-08-23'):
    """Return a list of temperature metrics from a given start date to the last date"""
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    def calc_temps(start_date, end_date):
        """Return a list of temperature metrics from a given start date to a given end date"""
        # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
        # Query all measurements from the dates provided
        results = session.query(Measurement.tobs).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
        
        # Convert list of tuples into normal list
        all_results = np.ravel(results)

        # Convert results to respective functions of TMIN, TAVG, and TMAX
        tmin = np.min(all_results)
        tavg = np.average(all_results)
        tmax = np.max(all_results)
        return tmin, tavg, tmax

    tmin, tavg, tmax = calc_temps(start, end)
    results_dict = {"TMIN": tmin.astype(float), "TAVG": tavg.astype(float), "TMAX": tmax.astype(float)}

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    return jsonify(results_dict)

if __name__ == '__main__':
    app.run(debug=False)
