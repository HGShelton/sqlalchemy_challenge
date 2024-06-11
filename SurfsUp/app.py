# Import the dependencies.
from flask import Flask, jsonify

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

from datetime import datetime, timedelta
import datetime as dt

import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
Base.classes.keys()

# Save references to each table
stations = Base.classes.station
measurements = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def routes():
    """List all available routes."""
    return(
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Design a query to retrieve the last 12 months of precipitation data and plot the results. 
    # Starting from the most recent data point in the database. 
    recent_date = datetime.strptime('2017-08-23', '%Y-%m-%d')

    # Calculate the date one year from the last date in data set.
    one_year_ago = recent_date - dt.timedelta(days=366)
    
    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(measurements.date, measurements.prcp).\
                    filter(measurements.date >= one_year_ago).all()
    
    # Create a dictionary with date as the key and precipitation as the value
    # Xpert Learning Assistant was used create a dictionary - prcp for date, prcp in precipitation_data}
    prcp_data = {date: prcp for date, prcp in precipitation_data}
    
    # Return the precipitation data as JSON
    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Design a query to list all stations
    results = session.query(measurements.station).distinct().all()

    # Convert list of tuples into normal list
    # ChatGpt was used to determine code needed to return JSON list
    station_list = list(np.ravel(results))

    # Return stations as JSON
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    temps = [measurements.station,
         func.min(measurements.tobs),
         func.max(measurements.tobs),
         func.avg(measurements.tobs)]
    
    most_active_temps = session.query(*temps).\
        filter(measurements.station == 'USC00519281').\
        group_by(measurements.station).\
        order_by(measurements.station).all()
    
    # Return JSON list of tobs for the previous year
    temp_stats = list(np.ravel(most_active_temps))
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>")
def temperature_start(start):
    # Determine the minimum temperature, the average temperature, and the maximum temperature for a specified start date
    start_date = datetime.strptime(start, '%Y-%m-%d')

    temperature_data = session.query(measurements.date, measurements.tobs).filter(measurements.date >= start_date).all()

    # Xpert Learning Assistant was used to determine code error when entering temperature data into a listt - temperatures = [data[1] for data in temperature_data]
    temperatures = [data[1] for data in temperature_data]

    min_temp = np.min(temperatures)
    avg_temp = np.mean(temperatures)
    max_temp = np.max(temperatures)

    # Xpert Learning Assistant was used to determine value for key:
    temp_stats = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }

    # Return a JSON list
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start, end):
    # Determine the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range
    start_date = datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.strptime(end, '%Y-%m-%d')

    temperature_data = session.query(measurements.date, measurements.tobs).filter(measurements.date.between(start_date, end_date)).all()

    temperatures = [data[1] for data in temperature_data]

    min_temp = np.min(temperatures)
    avg_temp = np.mean(temperatures)
    max_temp = np.max(temperatures)

    temp_stats = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }

    # Return a JSON list
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True) 