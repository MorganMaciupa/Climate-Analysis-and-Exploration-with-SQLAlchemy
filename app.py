
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

from flask import Flask, jsonify

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

@app.route("/")
def homepage(): #List all routes that are available
    return (
        f"<h1>Welcome to Morgan's Climate App API!</h1><br/>"
        f"<h2>Available Routes:</h2><br/><br/>"
        f"Return the precipitation data for the last 12 months:<br/>"
        f"/api/v1.0/precipitation<br/><br/>"
        f"Return a lis tof all staitons in the dataset:<br/>"
        f"/api/v1.0/stations<br/><br/>"
        f"Return the dates and temperature observations of the most active station for the last year of data:<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date<br/>"
        f"Calculates TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.<br/>"
        f"Enter date in the format YYYY-MM-DD<br/>"
        f"/api/v1.0/<start><br/><br/>"
        f"Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start-end range<br/>"
        f"Calculates the TMIN, TAVG, and TMAX for dates between the start and end date inclusive<br/>"
        f"Enter date in the format YYYY-MM-DD/YYYY-MM-DD<br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation(): # JSON representation of precipitation dictionary.
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    
    precip = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > query_date).\
        order_by(measurement.date).all()
    
    prcp_rows = [{"Date": result[0], "Precip": result[1]} for result in precip]
    
    return jsonify(prcp_rows)

@app.route("/api/v1.0/stations")
def stations(): # JSON representation of all_stations dictionary.
# Return a JSON list of stations from the dataset.
    all_stations = engine.execute('SELECT * FROM station').fetchall()

    station_dict = [{"ID": result[0],
                 "Station": result [1],
                 "Name": result[2],
                 "Latitude": result[3],
                 "Longitude": result[4],
                 "Elevation": result[5]} for result in all_stations]
    
    return jsonify(station_dict)

@app.route("/api/v1.0/tobs")
def tobs(): # JSON representation of dates and temperature observations of the most active station for the last year of data.
#Query the dates and temperature observations of the most active station for the last year of data.
    tobs_activity = session.query(measurement.station,
        func.count(measurement.tobs)
        ).group_by(measurement.station
        ).order_by(func.count(measurement.station).desc())
        
    most_active_tobs = tobs_activity[0]
    tobs_station_name = most_active_tobs[0]

    tobs2 = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > query_date).\
        filter(measurement.station == tobs_station_name).\
        order_by(measurement.date).all()
        
    tobs_station_dict = [{"Station": most_active_tobs[0],
                        "Date": result[0], "TOBS": result[1]} for result in tobs2]
    
    return jsonify(tobs_station_dict)

@app.route("/api/v1.0/<date>")
def start_date_tobs(date):

    day_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= date).all()
    return jsonify(day_tobs_results)

@app.route("/api/v1.0/<start>/<end>")
def startDateEndDate(start,end):
    
    start_end_tobs_results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).all()
    return jsonify(start_end_tobs_results)

if __name__ == "__main__":
    app.run(debug=True)