VERSION_STR = 'v1.0.0'

import requests
import numpy as np
from error import Error
from flask import Blueprint, request, jsonify
from auto_completer import MyCompleter

blueprint = Blueprint(VERSION_STR, __name__)
auto_comp = MyCompleter()

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
      - name: positive_items
        in: query
        description: This is a list of items the user likes
        required: true
        type: array
        item:
           type: string
      - name: negative_items
        in: query
        description: This is a list of items the user DOES NOT like
        required: true
        type: array
        item:
           type: string

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded
    '''
    d = {'results': [{'brewery': 'Four Peaks', \
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
    return jsonify(d)

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
      - name: city
        in: query
        description: This is the city the user wishes to get a list of breweries for
        required: true
        type: array
        item:
           type: string

    consumes:
      - multipart/form-data
      - application/x-www-form-urlencoded
    '''
    location_only_results = {'results': [{'name': 'Four Peaks',
                        'longitude': '97.000',
                        'latitude': '-107.9',
                        'overall_rating': '97.5'},
                        {'name': 'Sonoran Brewing Company',
                        'longitude': '95.000',
                        'latitude': '-109.9',
                        'overall_rating': '94.5'}]}
    return jsonify(location_only_results)

from app import app
app.register_blueprint(blueprint, url_prefix='/'+VERSION_STR)
