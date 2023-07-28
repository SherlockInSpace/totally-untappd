#!/usr/bin/python3

from multiprocessing.pool import ThreadPool
import concurrent.futures

import json
import requests
import requests_random_user_agent
import time

class TotalWine:

    def __init__(self, storeId, state):
        self.storeId = storeId
        self.state = state

    ### Creates a Total Wine URL based on the storeId and state, including the
    ### the department we are searching as well
    def __createTotalWineUrl(self, storeId, state, department, pageSize, pageNo=1):
        return \
        'https://www.totalwine.com/search/api/product/categories/v2/categories/c0010/products?' \
        + f'page={pageNo}&' \
        + f'pageSize={pageSize}&' \
        + f'state=US-{state}&' \
        + 'shoppingMethod=INSTORE_PICKUP&' \
        + 'userShoppingMethod=INSTORE_PICKUP&' \
        + 'allStoresCount=true&' \
        + f'storeId={storeId}&' \
        + f'department={department}&' \
        + 'instock=true&' \
        + 'batch=true'

    ### Searches a particular store in a particular department on a particular
    ### HTML page number
    def __getTotalWineDepartmentPage(self, department, pageSize, pageNo):
        while(1):
            url = self.__createTotalWineUrl(
                    self.storeId,
                    self.state,
                    department,
                    pageSize,
                    pageNo)
            response = requests.get(url, headers={'Cache-Control' : 'no-cache'})
            if response.status_code == 403:
                # We were probably blocked, so try again
                # Using the random agents we should be able to get through
                continue
            elif response.status_code == 429:
                time.sleep(1)
                continue
            break

        data = json.loads(response.content)
        return data


    def searchTotalWineStore(self, department, pageSize = 200):
        result = self.__getTotalWineDepartmentPage(department, pageSize, 1)

        # Okay, we've got the first page which tells us how many more pages
        # there are to search
        totalPages = result['pagination']['totalPages']
        beerList = []
        for beer in result['products']:
            beerList.append(beer)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for pageNo in range(2, totalPages + 1, 1):
                futures.append(executor.submit(
                    self.__getTotalWineDepartmentPage, department, pageSize, pageNo))
            for future in concurrent.futures.as_completed(futures):
                for beer in future.result()['products']:
                    beerList.append(beer)

        return beerList