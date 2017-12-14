import os
import requests

base_yelp_url = 'https://api.yelp.com/v3/businesses/search'
headers = {'Authorization': 'Bearer ' + os.environ['YELP_API_KEY']}
params = {'term': 'food', 'limit': 50}

def get_food_at_location(location):
    if invalid(location):
        return None
    params['location'] = location
    resp = requests.get(base_yelp_url, params=params, headers=headers)
    return resp

def invalid(value):
    return value == None or value == '' or type(value) != str
