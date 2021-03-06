from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime as dt
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

# config for DB schematics
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Location(db.Model):
    """docstring for Location."""
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=dt.utcnow())

    def __init__(self, location):
        self.location = location

    def __repr__(self):
        return '<Location %s>' % self.location

    def __str__(self):
        return '%s' % self.location

@app.route('/')
def home():
    return redirect('/yelp')

@app.route('/yelp', methods=['POST', 'GET'])
def yelp():
    if request.method == 'POST':
        if request.form:
            final_add = construct_address(
                request.form['address'],
                request.form['city'],
                request.form['state'],
                request.form['zip']
            )
            response = api_helper.get_food_at_location(final_add)
            if response != None and response.status_code == 200:
                add_location_to_db(final_add)
                df = get_search_trend_vis(final_add)
                fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 5))
                ax0.plot(
                    df['index'].map(lambda x: x.strftime('%Y-%m-%d')).tolist(),
                    df[0].tolist(),
                    linestyle='None',
                    marker='o'
                )
                ax0.set_title('Searches for this location')
                final_stuff = response.json()
                businesses = final_stuff['businesses']
                ax1.hist(
                    x=get_all_ratings(businesses),
                    bins=30,
                    histtype='stepfilled'
                )
                ax1.set_title('Restaurant ratings at this location')
                top_six = get_n_businesses(6, businesses)
                return render_template('search.html', top_six=top_six, location=final_add, data=mpld3.fig_to_html(fig))
            return render_template('yelp.html', top_places=get_frequent_locations(5))
        return render_template('yelp.html', top_places=get_frequent_locations(5))
    else:
        return render_template('yelp.html', top_places=get_frequent_locations(5))

@app.route('/get_popular/<location>', methods=['GET'])
def get_popular(location):
    response = api_helper.get_food_at_location(location)
    if response != None and response.status_code == 200:
        add_location_to_db(location)
        df = get_search_trend_vis(location)
        fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 5))
        ax0.plot(
            df['index'].map(lambda x: x.strftime('%Y-%m-%d')).tolist(),
            df[0].tolist(),
            linestyle='None',
            marker='o'
        )
        ax0.set_title('Searches for this location')
        final_stuff = response.json()
        businesses = final_stuff['businesses']
        ax1.hist(
            x=get_all_ratings(businesses),
            bins=30,
            histtype='stepfilled'
        )
        ax1.set_title('Restaurant ratings at this location')
        top_six = get_n_businesses(6, businesses)
        return render_template('search.html', top_six=top_six, location=location, data=mpld3.fig_to_html(fig))
    return redirect('/yelp')

def construct_address(*args):
    return ' '.join(args).strip()

def get_n_businesses(n, businesses):
    best = get_normal_scores(n, businesses)
    top_n = []
    for business in businesses:
        if business['name'] in best.index:
            one_business = {}
            for key in business.keys():
                if key in ['name', 'url', 'image_url', 'rating', 'price']:
                    one_business[key] = business[key]
            top_n.append(one_business)
    return top_n

def get_all_ratings(businesses):
    return [business.get('rating') for business in businesses if business.get('rating') != None]

def get_normal_scores(n, businesses):
    raw_data = {}
    for business in businesses:
        columns = [business.get('price'), business.get('rating'), business.get('review_count')]
        if None not in columns:
            columns[0] = len(columns[0])
            raw_data[business.get('name')] = columns
    df = pd.DataFrame.from_dict(raw_data, orient='index')
    normal = (df - df.min()) / (df.max() - df.min())
    normal['score'] = normal[0] + normal[1] + normal[2]
    top_places = normal.nlargest(n, 'score')
    return top_places

# helper func for adding location to DB
def add_location_to_db(address):
    location = Location(address)
    db.session.add(location)
    db.session.commit()

# get the locations with the most searches
def get_frequent_locations(num_locations):
    locations = db.session.query(Location.location, db.func.count(Location.location).label('Searches'))\
        .group_by(Location.location)\
        .order_by(db.desc('Searches'))\
        .limit(num_locations)\
        .all()
    return locations

def get_location_trend(location):
    location_trends = db.session.query(db.func.DATE(Location.created_at).label('Date'), db.func.count(db.func.DATE(Location.created_at)).label('Searches'))\
        .filter(Location.location == location)\
        .group_by(db.func.DATE(Location.created_at))\
        .all()
    return location_trends

def get_search_trend_vis(location):
    location_trends = get_location_trend(location)
    before_df = {}
    for data in location_trends:
        before_df[data[0]] = data[1]
    df = pd.DataFrame.from_dict(before_df, orient='index')
    df = df.reset_index()
    return df

if __name__ == '__main__':
    app.run(debug=True)
