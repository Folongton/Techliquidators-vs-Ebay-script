import os           # we don't need it here, do we ?

import requests
import json


# print(endpoint)  # to get to actual request link

class Ebay:
    def __init__(self, apikey):    # initial function requires apikey
        self.apikey = apikey
        self.endpoin  = 'https://svcs.ebay.com/services/search/FindingService/v1' \
           '?OPERATION-NAME=findCompletedItems' \
           '&SERVICE-VERSION=1.0.0' \
           '&RESPONSE-DATA-FORMAT=JSON' \
           '&callback=_cb_findItemsByKeywords' \
           '&REST-PAYLOAD' \
           '&paginationInput.entriesPerPage=100' \
           '&GLOBAL-ID=EBAY-US&siteid=0' \
           '&itemFilter(0).name=Condition' \
           '&itemFilter(0).value=Used' \
           '&SoldItemsOnly=true'

    def search(self, page=1, keyword=None):
        if keyword and page <= 100:   # what is keyword is true and keyword != ??? # If keyword means keyword is not None and  keyword!=''   Runs until keyword comes from Excel file, when hits '' it stops
            keyword = keyword.replace('&quot;', '')
            keyword = keyword.replace('&', ' ')
            print(f'API Request Keyword: {keyword}, Page fetching: {page}')
            response = requests.get(
                f'{self.endpoin}&SECURITY-APPNAME={self.apikey}&keywords={keyword}&paginationInput.pageNumber={page}')   # why self.apikey , not apikey ???
            return self.parse(response.text, page)                # what is Parsing -> https://www.quora.com/What-does-parsing-in-programming-mean
        else:                                                     # HTML Parsing -> https://stackoverflow.com/questions/20421316/what-does-html-parsing-mean
            return False, []

    def parse(self, json_, page):    # format Jason specified in our endpoint. About json decryption/encryption -> https://realpython.com/python-json/
        has_pages = False            # Need Explanation on a whole block parse...
        prices = []
        json_ = json.loads(json_.replace('/**/_cb_findItemsByKeywords(', '')[:-1])  # SLIce NOTATION = replaces begining of json text and returns alltext, but the last character ')' - > https://www.oreilly.com/learning/how-do-i-use-the-slice-notation-in-python
        if json_.get('findCompletedItemsResponse'):
            if json_['findCompletedItemsResponse'][0]['ack'][0] == 'Success':
                if int(json_['findCompletedItemsResponse'][0]['paginationOutput'][0]['totalPages'][0]) > page:
                    has_pages = True
                items = json_['findCompletedItemsResponse'][0]['searchResult'][0].get('item')
                if items:
                    for item in items:
                        prices.append(float(item['sellingStatus'][0]['currentPrice'][0]['__value__']))
        else:
            print('error', json_)
        return has_pages, prices
