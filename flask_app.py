from flask import Flask
from flask import render_template
from flask import request
from flask import redirect

import os
import scrapy
import urllib.parse as urlparse
import psycopg2

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

print(scrapy.scrap())
