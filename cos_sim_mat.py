from pymongo import MongoClient
from collections import defaultdict
import pandas as pd
from write_to_sql import BrewHoundDatabase
from sklearn.metrics.pairwise import cosine_similarity
import cPickle as pickle
import numpy as np

psql_db_connection = BrewHoundDatabase()

def name_input(beer_pref_list):
    beer_ids = list()
    for item in engine.execute("SELECT * FROM beer_names WHERE name IN {}".format(beer)):
            beer_ids.append(str(item[1]))

    return pd.read_sql("SELECT * FROM feature_matrix_2 WHERE id IN {}".format(tuple(beer_ids)),engine)

def find_local_beers(zip_code = None, city = None):
    zips_ = list()
    if zip_code:
        zips = get_tangental_zips(zip_code)
        for item in engine.execute("SELECT DISTINCT(beer_id) FROM beer_brew_loc WHERE zip_code IN {}".format(tuple(zips))):
            zips_.append(str(item[0]))
        return pd.read_sql("SELECT * FROM feature_matrix_2 WHERE id IN {}".format(tuple(zips_)),engine)
    if city:
        for item in engine.execute("SELECT DISTINCT(beer_id) FROM beer_brew_loc WHERE city LIKE '%{}%'".format(city)):
            zips_.append(str(item[0]))
        return pd.read_sql("SELECT * FROM feature_matrix_2 WHERE id IN {}".format(tuple(zips_)),engine)

def _get_tangental_zips(zip_code, miles = 5):
    close_zips = []
    api_key = 'uAQrm3UvHNo6NuntpnTkFo52rnHRSZqnzhPWkJr2xP9kkwNKUG5z5aBxxioqhPNR'
    for zipper in  requests.get('https://www.zipcodeapi.com/rest/{}/radius.json/{}/{}/mile'.format(api_key,zip_code, miles)).json()['zip_codes']:
        close_zips.append(str(zipper['zip_code']))
    return close_zips

if __name__ == '__main__':
    cos_sim, ids = create_cos_mat()
    pickle_cos_mat(cos_sim, ids)
