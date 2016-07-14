from collections import defaultdict, Counter
import pandas as pd
from read_write_to_sql import BrewHoundDatabase
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import requests


class recommendBeers():

    def __init__(self, psql_conn):
        if isinstance(psql_conn, BrewHoundDatabase):
            self.psql_db = psql_conn
            self.zips = None
            self.city = None
            self.beer_names = self.psql_db.query_sql("SELECT * \
                                                           FROM beer_names")
            self.cat_info = self.psql_db.query_sql("SELECT name, id \
                                                           FROM category_info")
            self.style_info = self.psql_db.query_sql("SELECT name, id \
                                                           FROM style_info")
        else:
            return 'Please pass in a valid database connection'

    def recommend_controller(self, beer_pref_list, zip_code = None, city = None):
        #put Beer names in memeory
        #returns DF of preferred beers feature matrix
        pref_beer_ids = self.name_input(beer_pref_list)
        #returns DF of local beers feature matrix
        local_beer_ids = self._find_local_beers(zip_code, city)
        #returns cosine similarity matrix, arrays of pref & local beer IDs
        cos_sim_mat, pref_ids, loc_ids =  self._cos_sim(pref_beer_ids, local_beer_ids)
        #returns defautl dict of recommended beer ids & count of recommendation
        beer_counter = self._most_similar_beers(cos_sim_mat, loc_ids)
        return self._get_similar_beer_breweries_info(beer_counter, local_beer_ids)

    def name_input(self, beer_pref_list):

        temp_beer_id_df = self.beer_names['id'][self.beer_names.name.isin(beer_pref_list)].unique()
        beer_ids = [str(x) for x in temp_beer_id_df]

        # for item in self.psql_db.engine.execute("SELECT * \
        #                                          FROM beer_names \
        #                                          WHERE name IN {}".format(beer_pref_list)):
                # beer_ids.append(str(item[1]))

        return self.psql_db.query_sql("SELECT * \
                                       FROM feature_matrix_2 \
                                       WHERE id IN {}".format(tuple(beer_ids)))

    def _find_local_beers(self, zip_code = None, city = None):
        #List to store the unique beer IDs
        u_beer_id = list()
        #List to track brewery IDs
        u_brew_id = list()
        if zip_code:
            self.zips = tuple(self._get_tangental_zips(zip_code))
            for item in self.psql_db.engine.execute("SELECT DISTINCT(beer_id), brew_location_id \
                                                     FROM beer_brew_loc \
                                                     WHERE zip_code IN {}".format(self.zips)):
                u_beer_id.append(str(item[0]))
                u_brew_id.append(str(item[1]))

        elif city:
            self.city = city
            for item in self.psql_db.engine.execute("SELECT DISTINCT(beer_id), brew_location_id \
                                                     FROM beer_brew_loc \
                                                     WHERE LOWER(beer_brew_loc.city) LIKE '{}'".format(city.lower())):
                u_beer_id.append(str(item[0]))
                u_brew_id.append(str(item[1]))

        else:
            return 'Invalid entry, please try again'

        return self.psql_db.query_sql("SELECT * \
                                       FROM feature_matrix_2 \
                                       WHERE id IN {}".format(tuple(u_beer_id)))

    def _get_tangental_zips(self, zip_code, miles = 5):
        close_zips = []
        api_key = 'uAQrm3UvHNo6NuntpnTkFo52rnHRSZqnzhPWkJr2xP9kkwNKUG5z5aBxxioqhPNR'
        for zipper in  requests.get('https://www.zipcodeapi.com/rest/{}/radius.json/{}/{}/mile'.format(api_key,zip_code, miles)).json()['zip_codes']:
            close_zips.append(str(zipper['zip_code']))
        return close_zips

    def _cos_sim(self, pref_beers, local_beers):
        pref_ids = pref_beers['id']
        local_ids = local_beers['id']
        skinny_pref_beers = pref_beers.drop(['index','id'], axis = 1)
        skinny_local_beers = local_beers.drop(['index','id'], axis = 1)
        zero_fill_prefs = skinny_pref_beers.fillna(0)
        zero_fill_local = skinny_local_beers.fillna(0)
        #return the cosline similarity along with the beer_ids for each row/col index
        return cosine_similarity(zero_fill_prefs, zero_fill_local), pref_ids, local_ids

    def _most_similar_beers(self, cosine_matrix, local_brew_ids, similar_beers = 10):
        #Dictionary counting most similar beers
        beer_tracker = defaultdict(int)

        for row in np.argsort(cosine_matrix)[:,-similar_beers:]:
            for beer in local_brew_ids[row].values:
                beer_tracker[str(beer)]+=1

        return Counter(beer_tracker)

    def _get_similar_beer_breweries_info(self, beer_counts, feat_mat):

        recommended_beer_ids = tuple(beer_counts.keys())

        if self.zips:
            temp_df = self.psql_db.query_sql("SELECT DISTINCT(brew_location_id), beer_id \
                                          FROM beer_brew_loc \
                                          WHERE beer_id IN {} AND zip_code IN {}".format(recommended_beer_ids, self.zips))

            brewery_ids = tuple([str(x) for x in temp_df.brew_location_id.unique()])

        else:
            temp_df =  self.psql_db.query_sql("SELECT DISTINCT(brew_location_id), beer_id \
                                          FROM beer_brew_loc \
                                          WHERE beer_id IN {} \
                                          AND LOWER(beer_brew_loc.city) LIKE '{}'".format(recommended_beer_ids, self.city.lower()))

            brewery_ids = tuple([str(x) for x in temp_df.brew_location_id.unique()])

        brew_res = self.psql_db.query_sql("SELECT name1, city, state, zip_code, lat, long, brew_location_id \
                                       FROM brewery_info \
                                       WHERE brew_location_id IN {}".format(brewery_ids)).to_dict(orient='records')

        for brewery in brewery_ids:
            beer_brew_list = temp_df['beer_id'][temp_df['brew_location_id'] == brewery].unique()
            skinny_beer_df = feat_mat[feat_mat['id'].isin([str(x) for x in beer_brew_list])]
            temp_1 = pd.merge(skinny_beer_df, self.beer_names, left_on='id', right_on='id')
            temp_1.drop(['srmMin','srmMax','index_y','index_x','fgMax','fgMin','ogMin', 'abvMax','abvMin'], axis = 1, inplace = True)
            temp_2 = pd.merge(temp_1, self.style_info, left_on='styleId', right_on='id')
            temp_3 = pd.merge(temp_2, self.cat_info, left_on='category_id', right_on='id')
            temp_3.rename(columns = {'name_y':'category','name':'style','name_x':'beer_name'}, inplace = True)
            temp_3.drop(['id','id_x','id_y','category_id','styleId'], axis =1, inplace = True)
            temp_3.astype(unicode)
            temp_3['abv'] = temp_3['abv'].replace('nan', 'NA', regex = True)
            temp_3['ibus'] = temp_3['ibus'].replace('nan', 'NA', regex = True)
            temp_3.to_dict(orient='records')

            for brew_spa in brew_res:
                if brewery == brew_spa['brew_location_id']:
                    brew_spa['beers'] = temp_3.to_dict(orient='records')
                    brew_spa['brewery'] = brew_spa.pop('name1')
                else:
                    continue

        return {'response':brew_res}





if __name__ == '__main__':
    one =  ['"Mike Saw a Sasquatch" Session Ale','"Hey Victor" Smoked Porter','"EVL1" Imperial Red Ale','"Ah Me Joy" Porter','"God Country" Kolsch']
    two = 'Austin'

    beer_me = recommendBeers(BrewHoundDatabase())
    print beer_me.recommend_controller(one, city = two)
