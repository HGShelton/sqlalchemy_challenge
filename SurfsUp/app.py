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
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

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
def welcome():
    """List all available routes."""
    return(
        f"Available Routes:<br/>"
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



if __name__ == "__main__":
    app.run(debug=True) 