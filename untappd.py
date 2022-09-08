#!/usr/bin/python3

from curses import has_key
import requests
import csv
import brotli
import json
import re
import sys
import time
import urllib.parse
from time import sleep

from bs4 import BeautifulSoup

hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Accept' : 'application/json, text/plain, */*, application/x-www-form-urlencoded',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Cache-Control' : 'max-age=0'
}

untappdUrl = 'https://untappd.com/user/unzsuzsual/beers?q=Bloomin&sort=date'
'https://untappd.com/user/unzsuzsual/beers?q=Golden%20Road%20Brewing&sort=date'

csvHdr = [
    'name',
    'brand',
    'style',
    'abv',
    'ibu',
    'containerType',
    'price',
    'stock',
    'averageRating',
    'numberOfReviews',
    'zHasHad',
    'zRating',
]

def getAbvIbu(beer):
    name = beer['name']
    brewery = beer['brand']['name']
    if len(beer['categories']) < 4:
        style = 'None'
    else:
        style = beer['categories'][3]['name']

    untappdUrl = 'https://untappd.com/search?' + \
        urllib.parse.urlencode({'q' : name}, quote_via=urllib.parse.quote)

    req = requests.post(untappdUrl, headers=hdr)
    if req.status_code != 200:
        print('Failed to find beer {}, status = {}'.format(name, req.status_code))
        return

    # Status code is okay, but that doesn't mean we found matching beers
    # Now we parse the available list of beers
    soup = BeautifulSoup(req.text, 'html.parser')
    foundBeers = soup.find_all(class_='beer-item')
    matches = [None] * len(foundBeers)
    bestScore = 0
    bestBeer = None

    # print('DEBUG: Matched {} beers!'.format(len(foundBeers)))

    for idx in range(0, len(foundBeers), 1):
        found = foundBeers[idx]

        foundName = found.find(class_='name').getText()
        foundBrewery = found.find(class_='brewery').getText()
        foundStyle = found.find(class_='style').getText()
        
        # print('DEBUG: Name = {}, Brand = {}, Style = {}'.format(foundName, foundBrewery, foundStyle))

        score = 0
        if re.match(name, foundName) != None or re.match(foundName, name) != None:
            score = score + 1
        if re.match(style, foundStyle) != None or re.match(foundStyle, style) != None:
            score = score + 1
        if re.match(brewery, foundBrewery) != None or re.match(foundBrewery, brewery) != None:
            score = score + 1

        if score >= bestScore:
            bestScore = score
            bestBeer = found

        matches[idx] = [foundName, score]

    for match in matches:
        print('DEBUG: Beer {} score = {}'.format(match[0], match[1]))

    if bestBeer == None:
        results = {'abv' : 'None', 'ibu' : 'None'}
    else:
        abv = bestBeer.find(class_='abv').getText().strip()
        m = re.match('(.*)% ABV', abv)
        if m == None:
            abv = 'N/A'
        else:
            abv = m.group(1)
        ibu = bestBeer.find(class_='ibu').getText().strip()
        m = re.match('(.*)% IBU', ibu)
        if m == None:
            ibu = 'N/A'
        else:
            ibu = m.group(1)
        
        results = {
            'abv' : abv,
            'ibu' : ibu
        }
    
    return results

def findUntappedBeer(beer):
    name = beer['name']
    brewery = beer['brand']['name']
    if len(beer['categories']) < 4:
        style = 'None'
    else:
        style = beer['categories'][3]['name']

    untappdUrl = 'https://untappd.com/user/unzsuzsual/beers?' + \
        urllib.parse.urlencode({'q' : name}, quote_via=urllib.parse.quote) + \
        '&sort=date'
    # print('URL={}'.format(untappdUrl))
    req = requests.post(untappdUrl, headers=hdr)
    if req.status_code != 200:
        print('Failed to find beer {}, status = {}'.format(name, req.status_code))
        return
    
    # Status code is okay, but that doesn't mean we found matching beers
    # Now we parse the available list of beers
    soup = BeautifulSoup(req.text, 'html.parser')
    foundBeers = soup.find_all(class_='beer-item')
    matches = [None] * len(foundBeers)
    bestScore = 0
    bestBeer = None

    # print('DEBUG: Matched {} beers!'.format(len(foundBeers)))

    for idx in range(0, len(foundBeers), 1):
        found = foundBeers[idx]

        foundName = found.find(class_='name').getText()
        foundBrewery = found.find(class_='brewery').getText()
        foundStyle = found.find(class_='style').getText()
        
        # print('DEBUG: Name = {}, Brand = {}, Style = {}'.format(foundName, foundBrewery, foundStyle))

        score = 0
        if re.match(name, foundName) != None or re.match(foundName, name) != None:
            score = score + 1
        if re.match(style, foundStyle) != None or re.match(foundStyle, style) != None:
            score = score + 1
        if re.match(brewery, foundBrewery) != None or re.match(foundBrewery, brewery) != None:
            score = score + 1

        if score >= bestScore:
            bestScore = score
            bestBeer = found

        matches[idx] = [foundName, score]

    for match in matches:
        print('DEBUG: Beer {} score = {}'.format(match[0], match[1]))

    return False if bestBeer == None else True

with open('sheet.csv', 'w') as out:
    writer = csv.writer(out,
        delimiter = ',',
        quotechar = '"',
        doublequote = True,
        skipinitialspace = False,
        lineterminator = '\r\n',
        quoting = csv.QUOTE_MINIMAL)
    writer.writerow(csvHdr)

with open('beers.json', 'r', encoding='utf-8') as f:
    beerList = json.load(f)
    maxBeers = len(beerList['beers'])
    beerNo = 0
    for beer in beerList['beers']:
        print('(({}/{}) Searching for beer {}'.format(beerNo, maxBeers, beer['name']))
        beerNo = beerNo + 1
        time.sleep(1)
        zHasHad = findUntappedBeer(beer)
        # input("DEBUG: Press ENTER when ready to resume...")
        time.sleep(1)
        info = getAbvIbu(beer)
        if info == None:
            continue

        with open('sheet.csv', 'a') as out:
            writer = csv.writer(out, delimiter = ',',
                quotechar = '"',
                doublequote = True,
                skipinitialspace = False,
                lineterminator = '\r\n',
                quoting = csv.QUOTE_MINIMAL)

            if len(beer['categories']) < 4:
                style = 'None'
            else:
                style = beer['categories'][3]['name']

            row = [
                '{}'.format(beer['name']),
                '{}'.format(beer['brand']['name']),
                '{}'.format(style),
                '{}'.format(info['abv']),
                '{}'.format(info['ibu']),
                '{}'.format(beer['containerType']),
                '{}'.format(beer['price'][0]['price']),
                '{}'.format(beer['stockLevel'][0]['stock']),
                '{}'.format(beer['customerAverageRating']),
                '{}'.format(beer['customerReviewsCount']),
                '{}'.format(zHasHad),
                '0'
            ]
            writer.writerow(row)
            