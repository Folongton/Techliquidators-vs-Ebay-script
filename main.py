import os                   # interaction with OS ( powershell etc.)
import re                   # regular expressions module
from openpyxl import load_workbook, Workbook  # Importing Workbook Class and Read(load) existing logbook function from Openpyxl
from lot import Lot         # From file lot importing Class : Lot
import requests             # Library for HTML 1.1 requests from servers(websites)
from ebay import Ebay       # From file ebay import class Ebay
from consts import cat_url, directory, download_url # From file consts import variables ( Do we have to pull variables from the same project files?)
from database import Database   # From file database import Class Database
from helper import avg, median  # From file helper import Functions median and avg ( median formula questions ?)
from bs4 import BeautifulSoup   # Beautiful Soup is a Python library for pulling data out of HTML and XML files (why bs4 not BeautifulSoup?) Need more info on it.


auction_names = {} # Assigning Empty global variable as dictionary


def get_existed_items(db):
   ''' items = []
    for item in db.get('items', 'id'):
        items.append(int(item[0]))
    return items
    '''
   return [int(item[0]) for item in db.get('items', 'id')]   # function returns all items in DB. List . Refactoring (avoiding for loops) https://medium.com/python-pandemonium/never-write-for-loops-again-91a5a4c84baf


def get_new_items():                            # Function returns list of collected Auction ID's into items and adds ID:Title into auction_names dictionary
    html = requests.get(cat_url).text           # why .text ? -> It automatically decodes returned data to text format or it returns only TEXT part of request ???
    soup = BeautifulSoup(html, 'html.parser')   # standart soup object  https://www.youtube.com/watch?v=aIPqt-OdmS0
    items = []                                  # creates empty list
    losts = soup.find_all('div', class_='truncate-ellipsis')
    for lot in losts:
        name = lot.span.a.text                   # ???
        item = re.search('marketplace_main\.auction&amp;id=(\d+)"', str(lot)) # Auction number from link via RE https://regex101.com/
        if item:                                 #if item is True ???
            item = int(item.group(1))            # RE function  https://docs.python.org/2/library/re.html
            auction_names.update({item: name})   # how did we get name ?
            print(auction_names)                 # temporary print
            items.append(item)
    return list(set(items))                      # set function


def save_file(name, content):
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(f'{directory}/{name}.xlsx'):
        open(f'{directory}/{name}.xlsx', 'wb').write(content)


if __name__ == '__main__':                   # basically asks 'Is this file is being run directly from Python or it is being imported?' if yes... SO, if for any reason we will run this project from other file(module) this 'if' block will not execute. ----
                                             #https: // www.youtube.com / watch?v = sugvnHA7ElY & vl = en
    db = Database('techliquidators.sqlite')  # Create object db  - as in Database class def__init__

    existed_items = get_existed_items(db)
    new_items = get_new_items()
    new_items = [item for item in new_items if item not in existed_items]   # List. Refactoring (avoiding for loops) https://medium.com/python-pandemonium/never-write-for-loops-again-91a5a4c84baf

    # temp = []
    # for item in new_items:
    #     if item not in existed_items:
    #         temp.append(item)

    db.insert_many('items', new_items)      # Function from Database Class: inserts list of new auctions IDs into DB
    db.close()

    ebay = Ebay('VasylZhe-TechPric-PRD-2393f3dea-5cde0afe')     # Ebay class object as in __init__ Ebay

    for itemID in new_items:
        if not os.path.exists(f'{directory}/{itemID}.xlsx'):
            r = requests.post(download_url, {'auctionID': itemID})
            save_file(itemID, r.content)

    for file in os.listdir(directory):
        wb = Workbook()
        ws = wb.active

        ws.append(
            ['Auction Name', 'Auction ID', 'Lot ID', 'Reference ID', 'MFG Name', 'MFG Part Number', 'Title', 'BBY SKU',
             'UPC', 'Estimated MSRP', 'N of listings', 'AVG price by name EBay',
             'Median  price by name Ebay using high to low sorting', 'N of listings', 'Avg price by UPC Ebay',
             'Median price by UPC Ebay using  hight to low sorting', 'N of listings',
             'AVG price by MFG + Part Number Ebay',
             'Median price by MFG + Part Number Ebay using hight to low sorting'])

        id_ = int(file.replace('.xlsx', ''))
        lots = []
        temp_wb = load_workbook(f'{directory}/{file}')
        temp_ws = temp_wb.active
        for row in range(2, temp_ws.max_row + 1):
            values = []
            for column in range(1, temp_ws.max_column + 1):
                cell_obj = temp_ws.cell(row=row, column=column)
                values.append(cell_obj.value)
            lot = Lot(List=values)
            lot.fill_listings_by_Title(ebay)
            lot.fill_listings_by_MFG(ebay)
            lot.fill_listings_by_UPC(ebay)
            lots.append(lot)
            ws.append([auction_names.get(id_), lot.AuctionID, lot.LotID, lot.ReferenceID,
                       lot.MFGName, lot.MFGPartNumber, lot.Title, lot.BBYSKU,
                       lot.UPC, lot.EstimatedMSRP,
                       len(lot.listingsByTitle), avg(lot.listingsByTitle), median(lot.listingsByTitle),
                       len(lot.listingsByUPC), avg(lot.listingsByUPC), median(lot.listingsByUPC),
                       len(lot.listingsByMFG), avg(lot.listingsByMFG), median(lot.listingsByMFG)])
        index = ws.max_row + 1
        ws[f'L{index}'] = sum([avg(l.listingsByTitle) for l in lots])
        ws[f'M{index}'] = sum([median(l.listingsByTitle) for l in lots])
        ws[f'O{index}'] = sum([avg(l.listingsByUPC) for l in lots])
        ws[f'P{index}'] = sum([median(l.listingsByUPC) for l in lots])
        ws[f'R{index}'] = sum([avg(l.listingsByMFG) for l in lots])
        ws[f'S{index}'] = sum([median(l.listingsByMFG) for l in lots])
        # os.remove(f'{directory}/{file}')
        print('save file')
        wb.save(f'{directory}/{file}')

    #
    # temp_wb = load_workbook(BytesIO(r.content))
    # temp_ws = temp_wb.active
    # for row in range(temp_ws.max_row + 1):
    #     print(temp_ws['A1'].value)
