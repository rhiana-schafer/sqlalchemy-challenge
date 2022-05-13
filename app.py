import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Homepage!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/startdate/enddate<br/>")
        

@app.route("/api/v1.0/precipitation")
def json_prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_data = []
    for d, p in results:
        prcp_dict = {}
        prcp_dict["date"] = d
        prcp_dict["precipitation"] = p
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def json_stations():
    session = Session(engine)
    result = session.query(Station.name).all()
    session.close()
    stations = []
    for s in result:
        stations.append(s[0])
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
        # Return a JSON list of temperature observations (TOBS) 
        # for the previous year.
def json_tobs():
    session = Session(engine)
    #most active station
    station_activity = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()
    most_active_id = station_activity[0][0]
    #getting year dates
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    recent_date = dt.datetime.strptime(recent_date, '%Y-%m-%d')
    yearago_date = dt.date(recent_date.year-1, recent_date.month, recent_date.day)
    #Query the dates and temperature observations of the
        # most active station for the previous year of data.
    temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_id).\
        filter(Measurement.date > yearago_date).all()
    session.close()
    #convert into dict
    temp_data = []
    for d, t in temps:
        temp_dict = {}
        temp_dict["date"] = d
        temp_dict["temperature"] = t
        temp_data.append(temp_dict)
    return jsonify(temp_data)

@app.route("/api/v1.0/<start>")
        # When given the start only, 
        #   calculate TMIN, TAVG, and TMAX for all dates
        #   greater than or equal to the start date

def temp_summary_start(start):
    session = Session(engine)
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    #perform query
    temp_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_dt).all()
    session.close()
    #convert into right format to jsonify
    return_data = []
    for mini, max, avg in temp_summary:
        temp_dict = {}
        temp_dict["min"] = mini
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        return_data.append(temp_dict)
    return jsonify(return_data)

@app.route("/api/v1.0/<start>/<end>")
        # When given the start and the end date, 
        #    calculate the TMIN, TAVG, and TMAX for dates 
        #    from the start date through the end date (inclusive).
def temp_summary_start_end(start,end):
    end_dt = dt.datetime.strptime(end, '%Y-%m-%d')
    start_dt = dt.datetime.strptime(start, '%Y-%m-%d')
    session = Session(engine)
    #perform query
    temp_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_dt).\
        filter(Measurement.date < end_dt).all()
    session.close()
    #convert into right format to jsonify
    return_data = []
    for mini, max, avg in temp_summary:
        temp_dict = {}
        temp_dict["min"] = mini
        temp_dict["max"] = max
        temp_dict["avg"] = avg
        return_data.append(temp_dict)
    return jsonify(return_data)    


if __name__ == '__main__':
    app.run(debug=True)

#Hints: You will need to join the station and measurement 
# tables for some of the queries.
