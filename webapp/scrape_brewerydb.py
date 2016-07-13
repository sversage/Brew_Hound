from pymongo import MongoClient
import requests
import json

with open('/Users/marcversage/Desktop/Python_Content/API_Access/brewerydb.json', 'r') as f:
    api = json.loads(f.read())['api_key']

client = MongoClient()

database = client['beer_app']

def scrape_beer_data():
    collection = database['beers']
    for _ in range(1,1116):
        collection.insert_one(requests.get("http://api.brewerydb.com/v2/beers?p={}&withBreweries=y&withIngredients=Y&key={}}&srm=10".format(_,api)).json())

def scrape_category_data():
    collection = database['categories']
    collection.insert_one(requests.get('http://api.brewerydb.com/v2/categories?key=099fbac4e8dc7187b32d3624c1c870a8&srm=10').json())

def scrape_style_data():
    collection = database['styles']
    collection.insert_one(requests.get('http://api.brewerydb.com/v2/styles?key=099fbac4e8dc7187b32d3624c1c870a8&srm=10').json())

if __name__ == '__main__':
    #scrape_beer_data()
    #scrape_category_data()
    scrape_style_data()

client.close()
