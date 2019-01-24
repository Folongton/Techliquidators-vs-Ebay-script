import os

cat_url = 'https://techliquidators.com/tl/index.cfm?action=marketplace_main.list&condition=73&pageNumber=1&resultsPerPage=2'
download_url = 'https://techliquidators.com/tl/index.cfm?action=marketplace_main.spreadsheet'
directory = os.path.join(os.curdir, 'files')  # os.curdir - shows current directory. os.path.join - joins current directory+folder'files' ( creates folder'files' if absnt.
cache_db = 'cache.db'
