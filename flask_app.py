from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask import redirect

import matplotlib
matplotlib.use('Agg')

import os
import scrapy
import api_helper
import urllib.parse as urlparse
import psycopg2

import sys                             # system module
import pandas as pd                    # data package
import matplotlib.pyplot as plt, mpld3        # graphics module
import numpy as np                     # foundation for Pandas

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

class Location(db.Model):
    """docstring for Location."""
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text, nullable=False)

    def __init__(self, location):
        self.location = location

    def __rep__(self):
        return '<Location %s>' % self.location


@app.route('/')
def home():
    top_10 = scrapy.scrap()
    df = pd.DataFrame.from_dict(top_10, orient='index')
    fig = plt.figure()
    plt.bar(
        x=np.arange(len(df.index)),
        height=df[0],
        align='center',
        alpha=0.5,
        tick_label=df.index,
    )
    return render_template('index.html', data=mpld3.fig_to_html(fig))

@app.route('/yelp', methods=['POST'])
def yelp():
    if request.form:
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zip']
        print(address, city, state, zipcode)


    return render_template('yelp.html')

if __name__ == '__main__':
    app.run(debug=True)
