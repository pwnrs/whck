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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Location(db.Model):
    """docstring for Location."""
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text, nullable=False)

    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return '<Location %s>' % self.location

    def __str__(self):
        return '%s' % self.location

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
    return render_template('index.html', data=mpld3.fig_to_html(fig), top_places=get_frequent_locations(5))

@app.route('/yelp', methods=['POST', 'GET'])
def yelp():
    if request.method == 'POST':
        if request.form:
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            zipcode = request.form['zip']
            final_add = address + ' ' + city + ' ' + state + ' ' + zipcode
            final_add = final_add.strip()
            response = api_helper.get_food_at_location(final_add)
            if response != None and response.status_code == 200:
                add_location_to_db(final_add)
                final_stuff = response.json()
                businesses = final_stuff['businesses']
                top_six = get_n_businesses(6, businesses)
                return render_template('yelp.html', top_six=top_six)
            return render_template('yelp.html')
    else:
        return render_template('yelp.html')


@app.route('/get_popular/<location>', methods=['GET'])
def get_popular(location):
    response = api_helper.get_food_at_location(location)
    if response != None and response.status_code == 200:
        add_location_to_db(final_add)
        final_stuff = response.json()
        businesses = final_stuff['businesses']
        top_six = get_n_businesses(6, businesses)
        return render_template('yelp.html', top_six=top_six)
    return render_template('yelp.html')

def get_n_businesses(n, businesses):
    top_six = []
    for business in businesses[:n]:
        one_business = {}
        for key in business.keys():
            if key in ['name', 'url', 'image_url', 'rating', 'price']:
                one_business[key] = business[key]
        top_six.append(one_business)
    return top_six

def add_location_to_db(address):
    location = Location(address)
    db.session.add(location)
    db.session.commit()

def get_frequent_locations(num_locations):
    locations = db.session.query(Location.location, db.func.count(Location.location).label('Searches'))\
        .group_by(Location.location)\
        .order_by(db.desc('Searches'))\
        .limit(num_locations)\
        .all()
    return locations

if __name__ == '__main__':
    app.run(debug=True)
