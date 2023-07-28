#!/usr/bin/python3

import sqlite3

con = sqlite3.connect("totally-untappd.db")
cur = con.cursor()

cur.execute("""
    CREATE TABLE totalWine(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brewery TEXT NOT NULL,
            style TEXT,
            containerType TEXT,
            price REAL,
            stockLevel INTEGER,
            customerRating REAL,
            customerCount INTEGER,
            dateCreated TIMESTAMP,
            dateModified TIMESTAMP
    )""")

cur.execute("""
    CREATE TABLE untappd(
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            brewery TEXT NOT NULL,
            style TEXT,
            abv REAL,
            ibu REAL,
            rating REAL,
            totalWineId INTEGER NOT NULL,
            dateCreated TIMESTAMP,
            dateModified TIMESTAMP,
            FOREIGN KEY(totalWineId) REFERENCES totalWine(id)
    )""")

cur.execute("""
    CREATE TABLE untappdUser(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL,
            untappdId INTEGER,
            userRating REAL,
            dateCreated TIMESTAMP,
            dateModified TIMESTAMP,
            FOREIGN KEY(untappdId) REFERENCES untappd(id)
)""")

cur.execute("""
    CREATE TABLE totalWineStore(
            id INTEGER PRIMARY KEY,
            storeName TEXT NOT NULL,
            streetNumber INTEGER,
            streetName TEXT,
            city TEXT,
            state TEXT,
            zipCode INTEGER
)""")

# What Zsuzsa has had
cur.execute("""
    CREATE VIEW unzsuzsual
    AS
    SELECT
            untappd.name as "Beer",
            untappd.brewery AS "Brewery",
            untappd.style AS "Style",
            untappd.abv AS "ABV (%)",
            untappd.ibu AS "IBU",
            untappd.rating AS "Untappd Rating",
            untappdUser.userRating AS "User Rating",
            totalWine.customerRating AS "Total Wine Rating",
            totalWine.containerType AS "Container Type",
            totalWine.price AS "Price",
            totalWine.stockLevel AS "Stock"
    FROM
            untappdUser
            INNER JOIN untappd ON untappd.id = untappdUser.untappdId
            INNER JOIN totalWine ON totalWine.id = untappd.totalWineId
            INNER JOIN totalWineStore ON totalWine.
    WHERE untappdUser.userName = 'unzsuzsual'
""")

# What Zsuzsa has not had 
cur.execute("""
    CREATE VIEW available
    AS
    SELECT
            untappd.name as "Beer",
            untappd.brewery AS "Brewery",
            untappd.style AS "Style",
            untappd.abv AS "ABV (%)",
            untappd.ibu AS "IBU",
            untappd.rating AS "Untappd Rating",
            totalWine.customerRating AS "Total Wine Rating",
            totalWine.containerType AS "Container Type",
            totalWine.price AS "Price",
            totalWine.stockLevel AS "Stock",
            totalWineStore.storeName as "Store"
    FROM
            untappd
            INNER JOIN totalWine ON untappd.totalWineId = totalWine.id
            INNER JOIN totalWineStore ON totalWineStore.id = totalWine.totalWineStoreId
    WHERE untappd.id NOT IN
            (SELECT untappdUser.untappdId FROM untappdUser, untappd WHERE untappdUser.untappdId = untappd.id)
""")