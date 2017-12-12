from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

import os
import scrapy
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

if __name__ == '__main__':
    app.run(debug=True)



@app.route('/yelp')
def yelp():
    return render_template('yelp.html')
if __name__ == '__main__':
    app.run(debug=True)
