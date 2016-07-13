from pymongo import MongoClient
from collections import defaultdict, Counter
import pandas as pd
from write_to_sql import BrewHoundDatabase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests


class recommendBeers():

    def __init__(self, psql_conn):
        if isinstance(psql_conn, BrewHoundDatabase):
            self.psql_db = psql_conn
            self.zips = None
            self.city = None
        else:
            return 'Please pass in a valid database connection'

    def recommend_controller(self, beer_pref_list, zip_code = None, city = None):
        pref_beer_ids = self.name_input(beer_pref_list)
        local_beer_ids = self.find_local_beers(zip_code, city)
        cos_sim_mat, pred_ids, loc_ids =  self._cos_sim(pref_beer_ids, local_beer_ids)
        beer_counter = self._most_common_beers(cos_sim_mat, loc_ids)
        self._get_common_beer_breweries(beer_counter)

    def name_input(self, beer_pref_list):
        beer_ids = list()
        for item in self.psql_db.engine.execute("SELECT * \
                                                 FROM beer_names \
                                                 WHERE name IN {}".format(beer_pref_list)):
                beer_ids.append(str(item[1]))

        return self.psql_db.query_sql("SELECT * \
                                       FROM feature_matrix_2 \
                                       WHERE id IN {}".format(tuple(beer_ids)))

    def find_local_beers(self, zip_code = None, city = None):
        zips_ = list()
        if zip_code:
            self.zips = tuple(self._get_tangental_zips(zip_code))
            for item in self.psql_db.engine.execute("SELECT DISTINCT(beer_id) \
                                                     FROM beer_brew_loc \
                                                     WHERE zip_code IN {}".format(self.zips)):
                zips_.append(str(item[0]))
            return self.psql_db.query_sql("SELECT * \
                                               FROM feature_matrix_2 \
                                               WHERE id IN {}".format(tuple(zips_)))
        if city:
            self.city = city
            for item in self.psql_db.engine.execute("SELECT DISTINCT(beer_id) \
                                                     FROM beer_brew_loc \
                                                     WHERE LOWER(beer_brew_loc.city) LIKE '{}'".format(city.lower())):
                zips_.append(str(item[0]))
            return self.psql_db.query_sql("SELECT * \
                                               FROM feature_matrix_2 \
                                               WHERE id IN {}".format(tuple(zips_)))

    def _get_tangental_zips(self, zip_code, miles = 5):
        close_zips = []
        api_key = 'uAQrm3UvHNo6NuntpnTkFo52rnHRSZqnzhPWkJr2xP9kkwNKUG5z5aBxxioqhPNR'
        for zipper in  requests.get('https://www.zipcodeapi.com/rest/{}/radius.json/{}/{}/mile'.format(api_key,zip_code, miles)).json()['zip_codes']:
            close_zips.append(str(zipper['zip_code']))
        return close_zips


    def _cos_sim(self, pref_beers, local_beers):
        pref_ids = pref_beers.pop('id')
        local_ids = local_beers.pop('id')
        pref_beers.drop('index', axis = 1, inplace = True)
        local_beers.drop('index', axis = 1, inplace = True)
        zero_fill_prefs = pref_beers.fillna(0)
        zero_fill_local = local_beers.fillna(0)
        return cosine_similarity(zero_fill_prefs, zero_fill_local), pref_ids, local_ids

    def _most_common_beers(self, cosine_matrix, local_brew_ids, similar_beers = 20):
        beer_tracker = defaultdict(int)

        for row in np.argsort(cosine_matrix)[:,-similar_beers:]:
            for beer in local_brew_ids[row].values:
                beer_tracker[str(beer)]+=1

        return Counter(beer_tracker)

    def _get_common_beer_breweries(self, beer_counts):
        brewery_ids = set()
        if self.zips:
            for item in self.psql_db.engine.execute("SELECT DISTINCT(brew_location_id) \
                                                     FROM beer_brew_loc \
                                                     WHERE beer_id IN {} AND zip_code IN {}".format(tuple(beer_counts.keys()), self.zips)):
                brewery_ids.add(str(item[0]))

        else:
            for item in self.psql_db.engine.execute("SELECT DISTINCT(brew_location_id) \
                                                     FROM beer_brew_loc \
                                                     WHERE beer_id IN {} \
                                                        AND LOWER(beer_brew_loc.city) LIKE '{}'".format(tuple(beer_counts.keys()), self.city.lower())):
                brewery_ids.add(str(item[0]))

        for brewery in  self.psql_db.engine.execute("SELECT name1, city, state, zip_code, lat, long \
                                                 FROM brewery_info \
                                                 WHERE brew_location_id IN {}".format(tuple(brewery_ids))):
                print brewery


if __name__ == '__main__':
    one =  ('"Mike Saw a Sasquatch" Session Ale','"Hey Victor" Smoked Porter','"EVL1" Imperial Red Ale','"Ah Me Joy" Porter','"God Country" Kolsch')
    two = 'Austin'

    beer_me = recommendBeers(BrewHoundDatabase())
    print beer_me.recommend_controller(one, city = two)
