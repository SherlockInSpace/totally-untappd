#!/usr/bin/python3

import json

f = open('beers.json','r')

data = json.load(f)
beerList = {}

duplicateBeers = 0

for beer in data['beers']:
    if beer['id'] in beerList:
        print(f"Beer({}) {} is already in the list!")
        duplicateBeers = duplicateBeers + 1
        continue

    id = beer['id']
    beerList[id] = {
        "name" : beer['name'],
        "brand" : beer['brand']['name'],
        "category" : {
            "country_state" : beer['categories'][0]
        }
    }