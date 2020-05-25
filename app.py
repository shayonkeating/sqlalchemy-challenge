import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


latestquerydate = (session.query(measurement.date).order_by(measurement.date.desc()).first())

# extract string from query object
latestquerydate = list(np.ravel(latestquerydate))[0]

# convert to datetime object to work with it easier (year, month, day)
latestquerydate = dt.datetime.strptime(latestquerydate, '%Y-%m-%d')

# latestquerydate = dt.datetime.strftime(latestquerydate)
latestyear = int(dt.datetime.strftime(latestquerydate, "%Y"))
latestmonth = int(dt.datetime.strftime(latestquerydate, "%m"))
latestday = int(dt.datetime.strftime(latestquerydate, "%d"))

# calc one year before so now we have one year selected
lastyear = dt.date(latestyear, latestmonth, latestday)-dt.timedelta(days = 365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')



#################################################
# Home
#################################################

@app.route("/")
def home():
    return (f"Surfs up BRO<br/>"
            f"------------<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ all weather stations<br/>"
            f"/api/v1.0/precipitaton ~~ all precipitation data<br/>"
            f"/api/v1.0/temperature ~~ latest year of temp data<br/>"
            f"------------<br/>"
            f"datesearch: (yyyy-mm-dd)<br/>"
            f"/api/v1.0/datesearch/2015-05-30  ~~~~~~~~~~~ low, high, and average temp for each date<br/>"
            f"/api/v1.0/datesearch/2015-05-30/2016-01-30 ~~ low, high, and average temp for date<br/>"
            f"------------<br/>"
            f"---- data available from 2010-01-01 to 2017-08-23 ----<br/>"
            f"------------<br/>"

#################################################
# Stations
#################################################
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

            
#################################################
# Precipitaton
#################################################
@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)

#################################################
# Temperature
#################################################
@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > yearBefore)
                      .order_by(Measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)


            
            
            
#################################################
# Date Search
#################################################            
@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

            
            
@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

            
            
            

#################################################
# END AND RUN
#################################################
if __name__ == "__main__":
    app.run(debug=True)