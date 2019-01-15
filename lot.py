from consts import cache_db
import shelve  # DB for Cash


class Lot:
    def __init__(self, AuctionID=None, LotID=None, ReferenceID=None, MFGName=None, MFGPartNumber=None, Title=None,
                 BBYSKU=None, UPC=None, EstimatedMSRP=None, List=None):
        if List:
            self.AuctionID = List[0]
            self.LotID = List[1]
            self.ReferenceID = List[2]
            self.MFGName = List[3]
            self.MFGPartNumber = List[4]
            self.Title = List[5]
            self.BBYSKU = List[6]
            self.UPC = List[7]
            self.EstimatedMSRP = List[8]
        else:
            self.AuctionID = AuctionID
            self.LotID = LotID
            self.ReferenceID = ReferenceID
            self.MFGName = MFGName
            self.MFGPartNumber = MFGPartNumber
            self.Title = Title
            self.BBYSKU = BBYSKU
            self.UPC = UPC
            self.EstimatedMSRP = EstimatedMSRP
        self.listingsByTitle = []
        self.listingsByMFG = []
        self.listingsByUPC = []

    def fill_listings_by_Title(self, ebay):
        self.fill_listings(ebay, self.Title, self.listingsByTitle)

    def fill_listings_by_MFG(self, ebay):
        self.fill_listings(ebay, f'{self.MFGName} {self.MFGPartNumber}', self.listingsByMFG)

    def fill_listings_by_UPC(self, ebay):
        self.fill_listings(ebay, self.UPC, self.listingsByUPC)

    def fill_listings(self, ebay, param, obj):
        if param:
            with shelve.open(cache_db) as storage:
                cached = storage.get(param)
            if cached is not None:
                print(cached)
                obj.extend(cached)
            else:
                print('search')
                page = 1
                has_pages = True
                while has_pages:
                    has_pages, items = ebay.search(page, param)
                    obj.extend(items)
                    page += 1
                print(obj)
                with shelve.open(cache_db) as storage:
                    storage[param] = obj

    def __str__(self):
        return ' | '.join([f'{a}={getattr(self, a)}' for a in dir(self) if not a.startswith('__')])
