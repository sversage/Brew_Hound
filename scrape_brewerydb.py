from pymongo import MongoClient
import requests
import json

client = MongoClient()

database = client['beer_app']
collection = database['beers']

with open('brewerydb.json') as f:
    data = json.load(f)
    api = data['brew']

for _ in range(1,1116):
    collection.insert_one(requests.get("http://api.brewerydb.com/v2/beers?p={}&withBreweries=y&withIngredients=Y&key={}}&srm=10".format(_,api)))


client.close()
