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
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station

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
        f"/api/v1.0/start/2017-08-23<br/>"
        f"/api/v1.0/start/2017-08-23,2016-08-23"
    )


@app.route("/api/v1.0/precipitation")
def rain():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns Percipitation and Date Data"""
    # Query all passengers
    date = session.query(measurement).order_by(measurement.date.desc()).first().date
    datelist = list(date)
    datelist[3] = str(int(date[3])-1)
    datenew = ''.join(datelist)
    results = session.query(measurement.date,measurement.prcp).filter(measurement.date >= datenew).order_by(measurement.date).all()

    session.close()

    # pack data into dictionary
    all_rain = []
    for date, rain in results:
        rain_dict = {}
        rain_dict["key"] = date
        rain_dict["value"] = rain
        all_rain.append(rain_dict)
    # Convert list of tuples into normal list

    return jsonify(all_rain)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns station data"""
    # Query all unique stationds
    results =session.query(measurement.station).group_by(measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Returns the top station temperature data"""
    # get best station
    beststation = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    date = session.query(measurement).order_by(measurement.date.desc()).first().date
    datelist = list(date)
    datelist[3] = str(int(date[3])-1)
    datenew = ''.join(datelist)
    # Query all unique stationds
    results = session.query(measurement.date,measurement.tobs).filter(measurement.date >= datenew).filter(measurement.station == beststation[0][0]).order_by(measurement.date).all()
    session.close()

    # Convert list of tuples into normal list

    all_tobs= []
    for date, rain in results:
        tobs_dict = {}
        tobs_dict["key"] = date
        tobs_dict["value"] = rain
        all_tobs.append(tobs_dict)
    # Convert list of tuples into normal list

    return jsonify(all_tobs)

@app.route("/api/v1.0/start/<start_date>")
def start(start_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Returns min, max and avg after a given date."""
    # Query all unique stationds
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date >= start_date).all()
    session.close()

    stats = list(np.ravel(results))

    return jsonify(stats)

@app.route("/api/v1.0/start/<start_date>,<end_date>")
def startend(start_date,end_date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Returns min, max and avg after a given date."""
    # Query all unique stationds
    results = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).filter(measurement.date <= end_date).all()
    session.close()

    stats = list(np.ravel(results))

    return jsonify(stats)

if __name__ == '__main__':
    app.run(debug=True)
