#!/usr/bin/python3

from curses import has_key
import requests
import re
import requests_random_user_agent
import time
import urllib.parse
from time import sleep

from bs4 import BeautifulSoup

class Untappd:

    def __getAbv(self, beer):
        abv = beer.find(class_='abv').getText().strip()
        m = re.match('(.*)% ABV', abv)
        if m == None:
            abv = -1
        else:
            abv = m.group(1)

        if abv == "N/A":
            abv = -1
        return abv

    def __getIbu(self, beer):
        ibu = beer.find(class_='ibu').getText().strip()
        m = re.match('(.*) IBU', ibu)
        if m == None:
            ibu = -1
        else:
            ibu = m.group(1)
        
        if ibu == "N/A":
            ibu = -1
        return ibu

    def __createUntappdUrl(self, beerName, breweryName, userName=None):
        if userName == None:
            return 'https://untappd.com/search?' + \
                urllib.parse.urlencode(
                    {'q' : '{} {}'.format(breweryName, beerName)},
                    quote_via=urllib.parse.quote
                )
        else:
            return 'https://untappd.com/' \
                + f'user/{userName}/' \
                + 'beers?' \
                + urllib.parse.urlencode({'q' : '{} {}'.format(breweryName, beerName)}, quote_via=urllib.parse.quote) \
                + '&sort=date'

    def __retrieveURLData(self, url):
        req = None
        while(1):
            try:
                req = requests.post(url, headers={'Cache-Control' : 'no-cache'})
            except:
                print('Exception from Untappd. Sleeping until retry...')
                time.sleep(10)
                continue

            if req.status_code == 429:
                print(f'Untappd requested back off for {req.headers["Retry-After"]} seconds.')
                time.sleep(int(req.headers['Retry-After']))
                continue
            elif req.status_code != 200:
                print('Failed to find beer, status = {}'.format(req.status_code))
                return None
            break
        return req

    def __findBeer(self, beerName, breweryName, style):
        untappdUrl = self.__createUntappdUrl(beerName, breweryName)
        req = self.__retrieveURLData(untappdUrl)
        if req == None:
            return None

        # Status code is okay, but that doesn't mean we found matching beers
        # Now we parse the available list of beers
        soup = BeautifulSoup(req.text, 'html.parser')
        foundBeers = soup.find_all(class_='beer-item')
        if len(foundBeers) == 0:
            return None
        bestOption = {
            'score' : 0,
            'name' : None,
            'brewery' : None,
            'style' : None,
            'abv' : None,
            'ibu' : None,
            'id' : None
        }

        for idx in range(0, len(foundBeers), 1):
            found = foundBeers[idx]

            foundName = found.find(class_='name').getText()
            foundBrewery = found.find(class_='brewery').getText()
            foundStyle = found.find(class_='style').getText()
            foundId = found.find(class_='label')['href'].rsplit('/', 1)[-1]
            foundRating = found.find(attrs={'data-rating' : True})['data-rating']

            abv = self.__getAbv(found)
            ibu = self.__getIbu(found)

            score = 0
            if  re.compile(re.escape(beerName)).search(foundName) != None or\
                re.compile(re.escape(foundName)).search(beerName) != None:
                score = score + 1
            if  re.compile(re.escape(style)).search(foundStyle) != None or\
                re.compile(re.escape(foundStyle)).search(style) != None:
                score = score + 1
            if  re.compile(re.escape(breweryName)).search(foundBrewery) != None or\
                re.compile(re.escape(foundBrewery)).search(breweryName) != None:
                score = score + 1
            if abv != None:
                score = score + 1
            if ibu != None:
                score = score + 1

            if score > bestOption['score']:
                bestOption['score'] = score
                bestOption['name'] = foundName
                bestOption['brewery'] = foundBrewery
                bestOption['style'] = foundStyle
                bestOption['abv'] = abv
                bestOption['ibu'] = ibu
                bestOption['id'] = foundId
                bestOption['rating'] = foundRating

        return bestOption

    def searchForBeer(self, beerName, breweryName, style='None'):
        beer = self.__findBeer(beerName, breweryName, style)
        return beer

    def userHasHadBeer(self, userName, beerName, breweryName, style='None', id=None):
        beer = self.__findBeer(beerName, breweryName, style)
        if beer == None:
            return None

        untappdUrl = self.__createUntappdUrl(beerName, breweryName, userName)
        req = self.__retrieveURLData(untappdUrl)
        if req == None:
            return None
        
        soup = BeautifulSoup(req.text, 'html.parser')
        foundBeers = soup.find_all(class_='beer-item', attrs={'data-bid': beer['id']})
        beer['userHasHad'] = False
        if len(foundBeers) != 0:
            beer['userHasHad'] = True
            userRating = foundBeers[0].find(attrs={'data-rating' : True})['data-rating']
            beer['userRating'] = userRating

        beer['returnId'] = id
        return beer