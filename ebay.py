import os           

import requests
import json


# print(endpoint)  

class Ebay:
    def __init__(self, apikey):    
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
        if keyword and page <= 100:   
            keyword = keyword.replace('&quot;', '')
            keyword = keyword.replace('&', ' ')
            print(f'API Request Keyword: {keyword}, Page fetching: {page}')
            response = requests.get(
                f'{self.endpoin}&SECURITY-APPNAME={self.apikey}&keywords={keyword}&paginationInput.pageNumber={page}')   
            return self.parse(response.text, page)               
        else:                                                    
            return False, []

    def parse(self, json_, page):     
        has_pages = False            
        prices = []
        json_ = json.loads(json_.replace('/**/_cb_findItemsByKeywords(', '')[:-1])   
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
