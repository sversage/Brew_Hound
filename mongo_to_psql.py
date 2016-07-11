from pymongo import MongoClient
from collections import defaultdict
import pandas as pd
from write_to_sql import BrewHoundDatabase

#establish mongo connection
client = MongoClient()
database = client['beer_app']
collection = database['beers']

psql_db_connection = BrewHoundDatabase()

#creat dictionaries to track info being parsed
beer_id_name_lookup_table = defaultdict(list)
brewery_id_name_lookup_table = defaultdict(list)
feature_dict = defaultdict(list)
beer_brew_loc_map = defaultdict(list)

def mongo_query():
    mongo_results = collection.find({'data':{'$exists': 'true'}},{'data':True,'_id':False})
    for page in mongo_results:
        _beer_name_lookup(page)
        _brewery_name_lookup(page)
        _create_feature_matrix(page)
        _beer_brewery_loc_mapping(page)

def _create_feature_matrix(page):
    """Function to query MongoDB for the beer reviews to create a feature matrix
        by beer
    """
    features = ['originalGravity','abv','ibu','glasswareId','styleId','isOrganic','servingTemperature','style']
    style_features = ['abvMax','abvMin','srmMin','srmMax','fgMin','fgMax','ogMin','ogMax','ibuMin','ibuMax']

    #iterate through documents returned
    for beer in page['data']:
        try:
            #try drops beers without a brewery
            beer['breweries']
            feature_dict['id'].append(beer['id'])
            for feat in features:
                if feat == 'style':
                    try:
                        #try inserts none for beers that don't have a category feature
                        feature_dict['category_id'].append(beer[feat]['category']['id'])
                    except:
                        feature_dict['category_id'].append(None)
                    for steez in style_features:
                        try:
                            #try inserts none for beers that don't have a style feature
                            feature_dict[steez].append(beer[feat][steez])
                        except:
                            feature_dict[steez].append(None)
                else:
                    try:
                        #try inserts none for beers that don't have a feature
                        feature_dict[feat].append(beer[feat])
                    except:
                        feature_dict[feat].append(None)
        except:
            pass

def _beer_name_lookup(page):
    for beer in page['data']:
        try:
            beer_id_name_lookup_table['id'].append(beer['id'])
            beer_id_name_lookup_table['name'].append(beer['name'])
        except:
            pass

def _brewery_name_lookup(page):
    for beer in page['data']:
        try:
            for brewery in beer['breweries']:
                for info in brewery['locations']:
                    required_features = ['locality','region', 'longitude', \
                                        'latitude','countryIsoCode','postalCode',\
                                        'streetAddress']
                    has_all = True
                    for field in required_features:
                        has_all &= (info.get(field) != None)
                    if has_all:
                        brewery_id_name_lookup_table['name1'].append(brewery['name'])
                        brewery_id_name_lookup_table['name2'].append(info['name'])
                        brewery_id_name_lookup_table['brewey_master_id'].append(brewery['id'])
                        brewery_id_name_lookup_table['brew_location_id'].append(info['id'])
                        brewery_id_name_lookup_table['city'].append(info['locality'])
                        brewery_id_name_lookup_table['state'].append(info['region'])
                        brewery_id_name_lookup_table['long'].append(info['longitude'])
                        brewery_id_name_lookup_table['lat'].append(info['latitude'])
                        brewery_id_name_lookup_table['co_code'].append(info['countryIsoCode'])
                        brewery_id_name_lookup_table['zip_code'].append(info['postalCode'])
                        brewery_id_name_lookup_table['street_address'].append(info['streetAddress'])
        except:
            pass

def _beer_brewery_loc_mapping(page):
    for beer in page['data']:
        try:
            for brewery in beer['breweries']:
                for info in brewery['locations']:

                    required_features = ['id','postalCode']
                    has_all = True
                    for field in required_features:
                        has_all &= (info.get(field) != None)
                    if has_all:
                        beer_brew_loc_map['beer_id'].append(beer['id'])
                        beer_brew_loc_map['brew_location_id'].append(info['id'])
                        beer_brew_loc_map['zip_code'].append(info['postalCode'])
        except:
            pass

def dicts_to_df_to_sql():
    beer_df = pd.DataFrame(beer_id_name_lookup_table)

    brewery_df = pd.DataFrame(brewery_id_name_lookup_table)

    feat_df = pd.DataFrame(feature_dict)

    mapping_df = pd.DataFrame(beer_brew_loc_map)

    psql_db_connection.write_to_sql(brewery_df, 'brewery_info')
    psql_db_connection.write_to_sql(beer_df, 'beer_names')
    psql_db_connection.write_to_sql(feat_df, 'full_features', 'replace')
    psql_db_connection.write_to_sql(mapping_df, 'beer_brew_loc')

def main():
    mongo_query()
    dicts_to_df_to_sql()

if __name__ == '__main__':
    main()
