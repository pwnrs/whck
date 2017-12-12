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
    return render_template('index.html', data=mpld3.fig_to_html(fig))

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
            print(final_add)
            final_stuff = (api_helper.get_food_at_location(final_add)).json()
            # print(final_stuff['businesses'][0])

            businesses = final_stuff['businesses']

            i = 0

            top_six = []
            while(i < 6):
                one_business = {}
                print(i)
                one_b = businesses[i]
                one_business['name'] = one_b['name']
                one_business['url'] = one_b['url']
                one_business['img_url'] = one_b['image_url']
                one_business['rating'] = one_b['rating']
                one_business['price'] = one_b['price']
                top_six.append(one_business)
                i += 1
            print(top_six)



            return render_template('yelp.html', top_six=top_six)
    else :
        return render_template('yelp.html')


if __name__ == '__main__':
    app.run(debug=True)
