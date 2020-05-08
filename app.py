import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

from datetime import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Meas = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def Home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    results = session.query(Meas.date, Meas.prcp).all()
    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
   
    session = Session(engine)
    stations = session.query(Station.station).all()
    session.close()

    return jsonify(stations)


@app.route("/api/v1.0/temperature")
def temperature():

    session = Session(engine)

    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    tempyr = session.query(Meas.date, Meas.tobs).\
        filter(Meas.station == 'USC00519281').\
        filter(Meas.date >= year_ago).\
        order_by(Meas.date).all()

    session.close()

    return jsonify(tempyr)


@app.route("/api/v1.0/<start>")
def calc_temps(start):

    session = Session(engine)

    start_dt = dt.strptime(start, "%Y-%m-%d")
    
    start_results = session.query(func.min(Meas.tobs), func.avg(Meas.tobs), func.max(Meas.tobs)).\
        filter(Meas.date >= start_dt).all()
    
    session.close()
    
    starting_date = list(np.ravel(start_results))

    return jsonify(starting_date)


@app.route("/api/v1.0/<start>/<end>")
def calcSE_temps(start, end):

    session = Session(engine)

    start_dt = dt.strptime(start, "%Y-%m-%d")

    end_dt = dt.strptime(end, "%Y-%m-%d")
    
    start_end_results = session.query(func.min(Meas.tobs), func.avg(Meas.tobs), func.max(Meas.tobs)).\
        filter(Meas.date >= start_dt).filter(Meas.date <= end_dt).all()
    
    session.close()
    
    startend_date = list(np.ravel(start_end_results))

    return jsonify(startend_date)


if __name__ == '__main__':
    app.run(debug=True)
