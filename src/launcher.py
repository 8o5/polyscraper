import time

from polyphia.scrape import scrapeCollections, scrapeProducts
from polyphia.webhook import notify, startScanning
from utils.__init__ import __sites__, __version__
from utils.helpers import cls, color, colortime, config, findSites, placeholder

sites = set()

def clear():
    cls()
    print("  ██████  ██ ▄█▀ ██▓ ██▓\n▒██    ▒  ██▄█▒ ▓██▒▓██▒\n░ ▓██▄   ▓███▄░ ▒██▒▒██▒\n  ▒   ██▒▓██ █▄ ░██░░██░\n▒██████▒▒▒██▒ █▄░██░░██░\n▒ ▒▓▒ ▒ ░▒ ▒▒ ▓▒░▓  ░▓  \n░ ░▒  ░ ░░ ░▒ ▒░ ▒ ░ ▒ ░\n░  ░  ░  ░ ░░ ░  ▒ ░ ▒ ░\n      ░  ░  ░    ░   ░  ")
    print(color(style="cyan", text=f"\n{__version__}"))

clear()

option = input(f"[{color(style='purple', text='1')}] Start Monitoring\n[{color(style='purple', text='2')}] Credits\n\n")

clear()

if option == "1":

    print(f"\n{color(style='blue', text='STARTED WITH SETTINGS:')}")
    for key, value in config['settings'].items():
        print(key, ':', value)

    print()

    info = findSites()

    poly = info[0]
    babymetal = info[1]
    polyphia_query = info[2]
    babymetal_query = info[3]

    lengths = (
        {
        "polyphia": poly,
        "babymetal": babymetal,
            }
        )

    def initialize(sites):

        products = []
        all_products = []
        all_collections = []

        for i in sites:

            products = None

            if i == __sites__[0]: # polyphia

                collections = (scrapeCollections(site=i, list_collections=[], all_list_collections=[])) # collections and products only need to be scraped once per site

                if collections == []:
                    raise Exception("Failed scraping collections")

                all_collections.append(collections)

                products = scrapeProducts(site=i)

                if products is None:
                    raise Exception("Failed scraping products")

                all_products.append(products)


                for value in polyphia_query:

                    print(f"[{color(style='purple', text=i.capitalize())}] {color(style='green', text='SCANNING')} {products.get(value, placeholder).name}") 

                    if config["settings"]["webhooks"] == True:

                        startScanning(
                            product_image=products.get(value, placeholder).img, 
                            product_title=products.get(value, placeholder).name, 
                            link=value,
                            price=products.get(value, placeholder).price, 
                            status=products.get(value, placeholder).instock, 
                            site=i.capitalize(),
                            site_img=products.get(value, placeholder).site_img, 
                        )
                
                print()
        

            elif i == __sites__[1]: # babymetal

                collections = (scrapeCollections(site=i, list_collections=[], all_list_collections=[])) # collections and products only need to be scraped once per site

                if collections == []:
                    raise Exception("Failed scraping collections")

                all_collections.append(collections)

                products = scrapeProducts(site=i)

                if products is None:
                    raise Exception("Failed scraping products")

                all_products.append(products)

                for value in babymetal_query:

                    print(f"[{color(style='purple', text=i.capitalize())}] {color(style='green', text='SCANNING')} {products.get(value, placeholder).name}") 

                    if config["settings"]["webhooks"] == True:

                        startScanning(
                            product_image=products.get(value, placeholder).img, 
                            product_title=products.get(value, placeholder).name, 
                            link=value,
                            price=products.get(value, placeholder).price, 
                            status=products.get(value, placeholder).instock, 
                            site=i.capitalize(),
                            site_img=products.get(value, placeholder).site_img, 
                        )
                
                print()
            
            else:
                products = None
                raise Exception(f"failed to initialize {i} from {sites}")

        return all_products

    try:
        if lengths["polyphia"] > 0:
            sites.add("polyphia")
        
        if lengths["babymetal"] > 0:
            sites.add("babymetalstore")
    
    except:
        raise Exception(f"{lengths} are not bigger than 0")

    init = initialize(sites=sites)
    

    if init == None:
        raise Exception(f"init == {init}")
    
    products = init[0] 
    print("returned")
    time.sleep(3)


    while True:
        
        print(colortime())

        if lengths["polyphia"] > 0:
            for value in polyphia_query:

                if products.get(value, placeholder).instock == "IN STOCK": 
                    notify(products=products, current=value)
                    print(f"[{color(style='purple', text='Polyphia')}] [{color(style='green', text='IN STOCK')}] {products.get(value, placeholder).name}") 

                elif products.get(value, placeholder).instock == "OOS":
                    print(f"[{color(style='purple', text='Polyphia')}] [{color(style='fail', text='OUT OF STOCK')}] {products.get(value, placeholder).name}") 
            
            print(
                f"\n[{color(style='cyan', text='SYSTEM')}] Waiting {color(style='blue', text=config['settings']['cooldown'])} seconds\n"
            )
        
        if lengths["babymetal"] > 0:

            for value in babymetal_query:

                if products.get(value, placeholder).instock == "IN STOCK": 
                    notify(products=products, current=value)
                    print(f"[{color(style='purple', text='BABYMETAL')}] [{color(style='green', text='IN STOCK')}] {products.get(value, placeholder).name}") 

                elif products.get(value, placeholder).instock == "OOS":
                    print(f"[{color(style='purple', text='BABYMETAL')}] [{color(style='fail', text='OUT OF STOCK')}] {products.get(value, placeholder).name}") 
            
            print(
                f"\n[{color(style='cyan', text='SYSTEM')}] Waiting {color(style='blue', text=config['settings']['cooldown'])} seconds\n"
            )


        time.sleep(config["settings"]["cooldown"])