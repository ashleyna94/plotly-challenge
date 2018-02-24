# Dependencies
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import (Flask, render_template, jsonify, request, redirect)

# Flask Setup
app = Flask(__name__)

# Database Setup 
engine = create_engine("sqlite:///db/belly_button_biodiversity.sqlite")

# Reflect the existing database into a new model 
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
OTU = Base.classes.otu
Samples = Base.classes.samples
Samples_Metadata = Base.classes.samples_metadata

# Create session link from Python to the database
session = Session(engine)

# Create a route that renders index.html template
@app.route("/")
def home():
    """Return the dashboard homepage."""
    return render_template("index.html")

@app.route("/names")
def sample_names():
    """Returns a list of sample names."""
    sample_names_list = Samples.__table__.columns.keys()
    # sample_names.remove("otu_id")
    sample_names_list = sample_names_list[1:]

    return jsonify(sample_names_list)

@app.route("/otu")
def otu_descriptions():
    """Returns a list of OTU descriptions."""
    results = session.query(OTU.lowest_taxonomic_unit_found).all()

    otu_descriptions_list = [result[0] for result in results]

    return jsonify(otu_descriptions_list)

@app.route("/metadata/<sample>")
def metadata(sample):
    """Returns a JSON dictionary of sample metadata."""
    # Select statement 
    sel = [Samples_Metadata.SAMPLEID, Samples_Metadata.ETHNICITY, Samples_Metadata.GENDER, Samples_Metadata.AGE, Samples_Metadata.BBTYPE, Samples_Metadata.LOCATION]
    # df = pd.DataFrame(Samples_Metadata)
    # Make sure to convert to 
    # df = pd.to_numeric(sample_id[3:])

    results = session.query(*sel).filter(Samples_Metadata.SAMPLEID == sample[3:]).all()

    # Creata a new dictionary 
    metadata_dict = {}

    for result in results:
        metadata_dict["SampleID"] = result[0]
        metadata_dict["Ethnicity"] = result[1]
        metadata_dict["Gender"] = result[2]
        metadata_dict["Age"]= result[3]
        metadata_dict["BBType"] = result[4]
        metadata_dict["Location"] = result[5]

    return jsonify(metadata_dict)

@app.route("/wfreq/<sample>")
def washing_frequency(sample):
    """Returns an integer value for the weekly washing frequency 'WFREQ'."""
    # Select statement 
    sel = [Samples_Metadata.WFREQ]

    results = session.query(*sel).filter(Samples_Metadata.SAMPLEID == sample[3:]).all()

    washing_freq_value = [result[0] for result in results]

    return jsonify(washing_freq_value)

@app.route("/samples/<sample>")
def samples_data(sample):
    """Return a list of dictionaries containing sorted lists for 'otu_ids' and 'sample_values'."""
    biodiversity_samples = pd.read_csv("DataSets/belly_button_biodiversity_samples.csv")
    samples_data_df = pd.DataFrame(biodiversity_samples)
    samples_data_df = samples_data_df.sort_values(by=sample, ascending=0)

    test = [{
        "otu_ids": samples_data_df[sample].index.values, 
        "sample_values": samples_data_df[sample].values
    }]
    
    return jsonify(test)

if __name__ == "__main__":
    app.run()