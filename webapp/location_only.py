import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json

with open('/Users/marcversage/Desktop/Python_Content/API_Access/brew_mapping.json', 'r') as f:
    api_key = json.loads(f.read())['api_key']


def city_brew_query(citystate):
    brewery_ratings = defaultdict(list)
    form_city_state = citystate.lower().replace(' ','')
    breweries_content = requests.get('http://beermapping.com/webservice/loccity/{}/{}'.format(api_key, form_city_state))
    content = BeautifulSoup(breweries_content.content, 'html.parser')
    for brew_name, brew_id, status, zip_, phone in zip(content.findAll('name'), \
                                                         content.findAll('id'), \
                                                         content.findAll('status'), \
                                                         content.findAll('zip'), \
                                                         content.findAll('phone')):
        if status.string != 'Beer Store':
            temp_dict = dict()
            temp_dict['name'] = brew_name.string
            temp_dict['phone'] = phone.string
            temp_dict['zip'] = zip_.string
            temp_dict['location'] = brew_long_lat(brew_id.string)
            temp_dict['rating'] = brew_rating(brew_id.string)
            brewery_ratings['brewery_results'].append(temp_dict)
        else:
            pass

def brew_long_lat(id_):
    breweries_loc = requests.get('http://beermapping.com/webservice/locmap/{}/{}'.format(api_key,id_))
    content = BeautifulSoup(breweries_loc.content, 'html.parser')
    return (content.find('lat').string,content.find('lng').string)

def brew_rating(id_):
    rating_dict = {}
    brew_rating = requests.get('http://beermapping.com/webservice/locscore/{}/{}'.format(api_key,id_))
    content = BeautifulSoup(brew_rating.content, 'html.parser')
    rating_dict['overall'] = content.find('overall').string
    rating_dict['selection'] = content.find('selection').string
    rating_dict['service'] = content.find('service').string
    rating_dict['atmosphere'] = content.find('atmosphere').string
    rating_dict['food'] = content.find('food').string
    rating_dict['reviewcount'] = content.find('reviewcount').string
    return rating_dict

if __name__ == '__main__':
    city_brew_query('phoenix,az')
    print brewery_ratings
