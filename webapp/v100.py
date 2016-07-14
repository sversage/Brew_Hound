VERSION_STR = 'v1.0.0'

import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify
from auto_completer import MyCompleter
import location_only
from cos_sim_mat import recommendBeers
import read_write_to_sql
from read_write_to_sql import BrewHoundDatabase
import unidecode

blueprint = Blueprint(VERSION_STR, __name__)
auto_comp = MyCompleter()
beer_me = recommendBeers(BrewHoundDatabase())

@blueprint.route('/autocomplete', methods=['GET'])
def autocomplete():
    '''
    Easy autocomplete
    Use this endpoint to give you a bunch of autocompleted string from
    a short query string.
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: Returns a dictionary with one key 'response' and a value with a list of strings that autocomplete the query
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: q
        in: query
        description: The query partial string thing
        required: true
        type: string

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded
    '''
    search_terms = request.args['q']
    return jsonify(auto_comp.complete(search_terms))

@blueprint.route('/make_recommendation', methods=['GET'])
def make_recommendation():
    '''
    Make recommendation
    Take a list of items the user likes and a list of items the user doesn't like, and return
    a list of recommended items for that user.
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: Returns a dictionary with one key 'response' and a value with a list of dictionaries, each with info about one recommended item
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: preferred_beers
        in: query
        description: This is a list of items the user likes
        required: true
        type: array
        item:
           type: string
      - name: location
        in: query
        description: This is the city or zip code the user would like to search in
        required: true
        type: string


    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded
    '''
    d = {'results': [{'brewery': 'Four Peaks', \
                    'brew_location_id':'bYu87', \
                    'longitude': '97.000', \
                    'latitude': '-107.9', 'city':\
                    'Tempe', 'state':'Arizona',\
                    'zip_code':'85251',\
                    'beers':[{'beer_name':'Kilt Lifter',\
                                'category':'British Origin Ales',\
                                'style' :'Scottish-Style Light Ale',\
                               'abv':'6',\
                               'ibu':'15',}]},
                    {'brewery': 'Sonoran Brewing Company', \
                    'brew_location_id':'cdFR45',
                    'longitude': '98.000', \
                    'latitude': '-105.9',
                    'city': 'Tempe',
                    'state':'Arizona',\
                    'zip_code':'85251',\
                    'beers':[{'beer_name':'Kilt Lifter',\
                                'category':'British Origin Ales',\
                                'style' :'Scottish-Style Light Ale',\
                               'abv':'6',\
                               'ibu':'15',}]}]}

    beer_preferences = eval(request.args['preferred_beers'])
    loc = request.args['location']

    try:
        loc = int(loc)
        return jsonify(beer_me.recommend_controller(beer_preferences, zip_code = loc))
    except:
        return jsonify(beer_me.recommend_controller(beer_preferences, city = loc))

@blueprint.route('/location_only_recommendation', methods=['GET'])
def location_only_recommendation():
    '''
    Make recommendation
    Take a string of the city the user would like to search and return near by breweries and their overall rating
    ---
    tags:
      - v1.0.0

    responses:
      200:
        description: Returns a dictionary with one key 'response' and a value with a list of dictionaries, each with info about one recommended item
      default:
        description: Unexpected error
        schema:
          $ref: '#/definitions/Error'

    parameters:
      - name: city,state
        in: query
        description: This is the city,state the user wishes to get a list of breweries for
        required: true
        type: array
        item:
           type: string

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded
    '''

    location = request.args['city,state']
    location_only.city_brew_query(location)
    return jsonify(location_only.brewery_ratings)


from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
