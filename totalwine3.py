#!/usr/bin/python3

from curses import has_key
import requests
import brotli
import json
import sys
import urllib.parse
from time import sleep

from bs4 import BeautifulSoup

PAGE_SIZE = 48
DEPARTMENT = 'Beer'

hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
    'Accept' : 'application/json, text/plain, */*',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive',
    'Cache-Control' : 'max-age=0'
}

totalWineUrl = \
'https://www.totalwine.com/search/api/product/categories/v2/categories/c0010/products?' \
+ 'page=1&' \
+ f'pageSize={PAGE_SIZE}&' \
+ 'state=US-CA&' \
+ 'shoppingMethod=INSTORE_PICKUP&' \
+ 'userShoppingMethod=INSTORE_PICKUP&' \
+ 'allStoresCount=true&' \
+ 'storeId=1106&' \
+ f'department={DEPARTMENT}&' \
+ 'instock=true&' \
+ 'batch=true'

response = requests.get(totalWineUrl, headers=hdr)

# NOTE: May not need this since requests automatically does decompression?
if (response.status_code == 403):
    print("AHH SHIT! We've been blocked!")
    sys.exit(-1)

if (response.headers['content-encoding'] != 'br'):
    print(f"ERROR! Expected brotli compression but got '{response.headers['content-encoding']}' instead!")
    sys.exit(-1)

data = json.loads(response.content)

totalPages = data['pagination']['totalPages']

beers = {}
duplicateBeers = 0
beerCount = 0

for pageNo in range(1, totalPages, 1):
    totalWineUrl = 'https://www.totalwine.com/search/api/product/categories/v2/categories/c0010/products?' \
        + f'page={pageNo}&' \
        + f'pageSize{PAGE_SIZE}=&' \
        + 'state=US-CA&' \
        + 'shoppingMethod=INSTORE_PICKUP&' \
        + 'userShoppingMethod=INSTORE_PICKUP&' \
        + 'allStoresCount=true&' \
        + 'storeId=1106&' \
        + f'department={DEPARTMENT}&' \
        + 'instock=true&' \
        + 'batch=true'
    
    response = requests.get(totalWineUrl, headers=hdr)
    if (response.status_code == 403):
        print("AHH SHIT! We've been blocked. Waiting for fix...")
        input("Press ENTER when ready to resume...")

    data = json.loads(response.content)

    for beer in data['products']:
        if beer['name'] in beers:
            print(f"{beer['name']} already entered!")
            print(f"{duplicateBeers} duplicate beers thus far...")
            duplicateBeers = duplicateBeers + 1
        else:
            with open('beers.json', 'a', encoding='utf-8') as f:
                json.dump(beer, f, ensure_ascii=False, indent=4)

    print(f"{pageNo}: Back off sleeping, in hopes we don't get blocked.")
    sleep(600)

print(f"A total of {len(beers.keys())} were added" \
    + f", of which {duplicateBeers} were duplicates")