from pymongo import MongoClient

client = MongoClient()
database = client['beer_app']
collection = database['beers']

out_file  = open('Brew_Hound/data/descriptions.txt', "wt")

description_count = 0
no_description_count = 0
total_count = 0

for page in collection.find():
    for beer in page['data']:
        total_count+=1
        try:
            out_file.write(beer['description'])
            description_count += 1
        except:
            no_description_count+=1

print 'Collected {} descriptions out of {} beers'.format(description_count, total_count)

out_file.close()
