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
    html = requests.get(cat_url).text           # why .text ? -> It automatically decodes returned data to text format or it returns only TEXT part of request ???  - ALL HTML
    soup = BeautifulSoup(html, 'html.parser')   # standart soup object  https://www.youtube.com/watch?v=aIPqt-OdmS0
    items = []                                  # creates empty list
    losts = soup.find_all('div', class_='truncate-ellipsis')
    for lot in losts:
        name = lot.span.a.text                   # lot.span.a.text - takes text from class_='truncate-ellipsis' on HTML page
        item = re.search('marketplace_main\.auction&amp;id=(\d+)"', str(lot)) # Auction number from link via RE https://regex101.com/. str(lot) changes object of bs4 lot to str.
        if item:                                 #if item is True ???
            item = int(item.group(1))            # RE function  https://docs.python.org/2/library/re.html
            auction_names.update({item: name})   # how did we get name ? - From name = lot.span.a.text
            print(auction_names)                 # temporary print
            items.append(item)
    return list(set(items))                      # set type onto -> list


def save_file(name, content):
    if not os.path.exists(directory):           # what if not ??? - False ?
        os.makedirs(directory)                  # why makedirs, not mkdir ?  Creates directory
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
            r = requests.post(download_url, {'auctionID': itemID})  # How did you figure out we can make post with data as :{'auctionID': itemID} ???
            save_file(itemID, r.content)                           # r.content - content of response in bytes

    for file in os.listdir(directory):    # for loop going over all files in given directory
        wb = Workbook()                   # creates workbook. standard openpyxl module object. GREAT EXAMPLES HERE: -> https://medium.com/aubergine-solutions/working-with-excel-sheets-in-python-using-openpyxl-4f9fd32de87f
        ws = wb.active                    # Workbook.active() - makes 1st sheet in WB active

        ws.append(
            ['Auction Name', 'Auction ID', 'MFG Name', 'MFG Part Number', 'Title', 'UPC',
             'N', 'Name AVG price by name EBay', 'Name Median  price by name Ebay using high to low sorting',
             'N', 'MFG AVG price by MFG + Part Number Ebay', 'MFG Median (Median price by MFG + Part Number Ebay using hight to low sorting)',
             'N', 'UPC AVG price by UPC Ebay', 'UPC Median price by UPC Ebay using  hight to low sorting', ' '])    # appends top row for more details here: https://medium.com/aubergine-solutions/working-with-excel-sheets-in-python-using-openpyxl-4f9fd32de87f

        id_ = int(file.replace('.xlsx', ''))                       # to get an Auction ID we Replaces .xlsx with empty and make it integer
        lots = []                                                  # creates empty list lots
        temp_wb = load_workbook(f'{directory}/{file}')             # load_workbook opens every file in a given directory
        temp_ws = temp_wb.active                                   # .active makes 1st WS active
        for row in range(2, temp_ws.max_row + 1):                  # Iterates thru all rows with data. 2 - because we have 1st row with our columns names appended earlier
            values = []                                            # creates empty value list
            for column in range(1, temp_ws.max_column + 1):        # iterates thru all columns with data starting with 1st.
                cell_obj = temp_ws.cell(row=row, column=column)    # Assigns cell values to Cell_obj
                values.append(cell_obj.value)                      # Appends values to values list .value function from Openpyxl which gets or set value held in a cell.
            lot = Lot(List=values)
            lot.fill_listings_by_Title(ebay)
            lot.fill_listings_by_MFG(ebay)
            lot.fill_listings_by_UPC(ebay)
            lots.append(lot)
            ws.append([auction_names.get(id_), lot.AuctionID,
                       lot.MFGName, lot.MFGPartNumber, lot.Title, lot.UPC,
                       len(lot.listingsByTitle), avg(lot.listingsByTitle), median(lot.listingsByTitle),
                       len(lot.listingsByMFG), avg(lot.listingsByMFG), median(lot.listingsByMFG),
                       len(lot.listingsByUPC), avg(lot.listingsByUPC), median(lot.listingsByUPC)])
        index = ws.max_row + 1
        ws[f'H{index}'] = sum([avg(l.listingsByTitle) for l in lots])
        ws[f'I{index}'] = sum([median(l.listingsByTitle) for l in lots])
        ws[f'K{index}'] = sum([avg(l.listingsByMFG) for l in lots])
        ws[f'L{index}'] = sum([median(l.listingsByMFG) for l in lots])
        ws[f'N{index}'] = sum([avg(l.listingsByUPC) for l in lots])
        ws[f'O{index}'] = sum([median(l.listingsByUPC) for l in lots])

        index = ws.max_row + 2
        total_avg_upc = (sum([avg(l.listingsByUPC) for l in lots]) + sum([median(l.listingsByUPC) for l in lots]))/2
        ws[f'N{index}'] = '30% ROI:'
        ws[f'O{index}'] = total_avg_upc * 0.77
        ws[f'P{index}'] = '42% ROI:'
        ws[f'Q{index}'] = total_avg_upc * 0.7

        index = ws.max_row + 1
        ws[f'N{index}'] = 'Ebay 0.13 fee'
        ws[f'O{index}'] = total_avg_upc * 0.13
        ws[f'Q{index}'] = total_avg_upc * 0.13

        index = ws.max_row + 1
        ws[f'N{index}'] = 'Shipping'
        ws[f'O{index}'] = '200'
        ws[f'Q{index}'] = '200'

        index = ws.max_row + 1
        ws[f'N{index}'] = 'Earnings'
        ws[f'O{index}'] = total_avg_upc - (total_avg_upc * 0.77) - (total_avg_upc * 0.13) - 200
        ws[f'Q{index}'] = total_avg_upc - (total_avg_upc * 0.7) - (total_avg_upc * 0.13) - 200

        index = ws.max_row + 1
        ws[f'N{index}'] = 'ROI clean'
        ws[f'O{index}'] = ((total_avg_upc - (total_avg_upc * 0.77) - (total_avg_upc * 0.13) - 200) / total_avg_upc)*100
        ws[f'Q{index}'] = ((total_avg_upc - (total_avg_upc * 0.7) - (total_avg_upc * 0.13) - 200) / total_avg_upc)*100

        # os.remove(f'{directory}/{file}')
        print('save EXCEL file')
        wb.save(f'{directory}/{file}')

        os.chdir(r'D:\Study 2018\Python codes 2\Techliquidators script\files')
        saved_file = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in saved_file:
            os.rename(f, f'D:/Study 2018/Python codes 2/Techliquidators script/UNPROCESSED auctions/{f}')
            print(f'file(s): {f} moved to Folder: UNPROCESSED auctions')





    #
    # temp_wb = load_workbook(BytesIO(r.content))
    # temp_ws = temp_wb.active
    # for row in range(temp_ws.max_row + 1):
    #       print(temp_ws['A1'].value)