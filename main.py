#!/usr/bin/python3

from multiprocessing.pool import ThreadPool
import concurrent.futures

import datetime
import sqlite3
import totalwine
import untappd

def updateTotalWineTable(STORE_ID, STATE, DEPARTMENT):

    ## Find all the beers in the Total Wine store
    store = totalwine.TotalWine(STORE_ID, STATE)
    data = store.searchTotalWineStore(DEPARTMENT)

    ## Connect to the sqlite database
    con = sqlite3.connect('totally-untappd.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    ## Iterate over all the beers
    for beer in data:
        style = 'N/A'
        if len(beer['categories']) > 3:
            style = beer['categories'][3]['name']

        currentDateTime = datetime.datetime.now()
        cmd = """REPLACE INTO totalWine
        (
            id,
            name,
            brewery,
            style,
            containerType,
            price,
            stockLevel,
            customerRating,
            customerCount,
            totalWineStoreId,
            dateCreated,
            dateModified
        ) VALUES (
            {0},
            "{1}",
            "{2}",
            "{3}",
            "{4}",
            {5},
            {6},
            {7},
            {8},
            {9}
            "{10}",
            "{11}"
        )
        """.format(
            beer['id'],
            beer['name'],
            beer['brand']['name'],
            style,
            beer['containerType'],
            beer['price'][0]['price'],
            beer['stockLevel'][0]['stock'],
            beer['customerAverageRating'],
            beer['customerReviewsCount'],
            STORE_ID,
            currentDateTime,
            currentDateTime
        )

        # print(f'Executing command: {cmd}')
        try:
            cur.execute(cmd)
        except:
            continue

    con.commit()

def updateUntappdTable(userName):
    website = untappd.Untappd()

    con = sqlite3.connect('totally-untappd.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    results = cur.execute("SELECT * FROM totalWine")
    rows = results.fetchall()

    beerList = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        for row in rows:
            print(f'Searching for {row["name"]} by {row["brewery"]}')
            futures.append(executor.submit(
                website.userHasHadBeer,
                    userName,
                    row['name'],
                    row['brewery'],
                    row['style'],
                    row['id']
            ))
        for future in concurrent.futures.as_completed(futures):
            beerInfo = future.result()
            if beerInfo == None:
                print(f'Could not find beer on Untappd!')
                continue
            beerList.append(beerInfo)

    for beerInfo in beerList:
        currentDateTime = datetime.datetime.now()
        cmd = """REPLACE INTO untappd
            (
                id,
                name,
                brewery,
                style,
                abv,
                ibu,
                rating,
                totalWineId,
                dateCreated,
                dateModified
            ) VALUES (
                {0},
                "{1}",
                "{2}",
                "{3}",
                {4},
                {5},
                {6},
                {7},
                "{8}",
                "{9}"
            )
        """.format(
            beerInfo['id'],
            beerInfo['name'],
            beerInfo['brewery'],
            beerInfo['style'],
            beerInfo['abv'],
            beerInfo['ibu'],
            beerInfo['rating'],
            beerInfo['returnId'],
            currentDateTime,
            currentDateTime
        )
        # print(cmd)
        cur.execute(cmd)
        con.commit()

        if beerInfo['userHasHad'] == False:
            continue

        print(f'User {userName} has had beer!')
        cmd = """REPLACE INTO untappdUser
            (
                userName,
                untappdId,
                userRating,
                dateCreated,
                dateModified
            ) VALUES (
                "{0}",
                {1},
                {2},
                "{3}",
                "{4}"
            )
        """.format(
            userName,
            beerInfo['id'],
            beerInfo['userRating'],
            currentDateTime,
            currentDateTime
        )

        cur.execute(cmd)
        con.commit()

updateTotalWineTable(2303, 'CO', 'Beer')
updateUntappdTable('unzsuzsual')