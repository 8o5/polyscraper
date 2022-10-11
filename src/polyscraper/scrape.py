import enum
import sys
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup
import time

from polyscraper.__init__ import __collections__
from polyscraper.helpers import Product, config, headers
from polyscraper.webhook import dataError, newCollection


def scrapeProducts():

    data = requests.get(
        url="https://www.polyphia.com/collections/all",
        headers=headers,
        timeout=5,
    )

    data.raise_for_status()

    if data.status_code != 200:  # site response error handling

        if config["settings"]["webhooks"] == True:
            dataError(data=data.url)

        sys.exit(data.status_code)

    elif data.status_code == 200:

        all_products = []

        x = BeautifulSoup(data.content, "html.parser")

        all_products = x.findAll("div", class_="grid-view-item product-card")
        all_products.extend(x.findAll("div", class_="grid-view-item grid-view-item--sold-out product-card"))

        products = {}
        for product_data in all_products:
            data = {}

            img_location = product_data.contents[5].contents[1].contents[1].contents[1].attrs["data-src"]
            img_url = img_location.replace("{width}", "540")

            if product_data.contents[11].contents[7].contents[3].contents[1].contents[0] == "Sold out":
                instock = "OOS"
            else:
                instock = "IN STOCK"

            data.update(
                {
                    "name": product_data.contents[9].contents[0],
                    "url": product_data.contents[1].attrs["href"],
                    "img": f"https://{img_url[2:]}",
                    "instock": instock,
                    "price": product_data.contents[11].contents[1].contents[3].contents[1].contents[0][:-1]
                }
            )
            my_product = Product(data)
            products.update({f"https://www.polyphia.com{product_data.contents[1].attrs['href']}": my_product})

        return products


def scrapeCollections(list_collections, all_list_collections):

    data = requests.get(
        url="https://www.polyphia.com/collections/",
        headers=headers,
        timeout=5,
    )

    data.raise_for_status()

    if data.status_code != 200:  # site response error handling

        if config["settings"]["webhooks"] == True:
            dataError(data=data.url)

        sys.exit(data.status_code)

    elif data.status_code == 200:
        x = BeautifulSoup(data.content, "html.parser")

        all_collections = x.findAll("div", class_="collection-grid-item__title h3")

        filtered_collections = x.findAll("a", class_="collection-grid-item__link")

        for collection in all_collections:

            all_list_collections.append(str.strip(collection.text))

            if str.strip(collection.text) not in __collections__:

                name = str.strip(collection.text)
                url_loc = collection.parent.parent
                print("here") # debug
                time.sleep(3)

                if url_loc["href"] != "#":
                    newCollection(name=name, url=f"https://www.polyphia.com{url_loc['href']}")

                elif url_loc["href"] == "#":
                    newCollection(name=name, url=None)

        for collection in filtered_collections:

            if collection["href"] != "#":
                list_collections.append(collection["href"].split("/")[2])

        return (list(list_collections), list(all_list_collections))
