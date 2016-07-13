from pymongo import MongoClient

client = MongoClient()
database = client['beer_app']
collection = database['beers']

def collect_descriptions(file_):
    out_file  = open(file_, "wt")

    description_count = 0
    no_description_count = 0
    total_count = 0

    for page in collection.find({'data.description':{'$exists': 'true'}},{'data.description':True,'_id':False})
        for beer in page['data']:
            total_count+=1
            try:
                    out_file.write(beer['description'])
                description_count += 1
            except:
                no_description_count+=1
    out_file.close()

    return 'Collected {} descriptions out of {} beers.\
     {} beers did not have a description'\
     .format(description_count, total_count, no_description_count)

if __name__ == '__main__':
    print collect_descriptions("data/descriptions.txt")
