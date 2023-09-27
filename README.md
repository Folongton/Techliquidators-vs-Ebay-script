# Techliquidators-script
This project helped us with decision-making regarding betting prices on wholesale auctions for one of my ventures.
Completed in 2019.

Business Goal : Analyze data from wholesale website and Ebay to determine maximum price we can pay for a lot with a given profitability expectation. 
#### Implementation : 
- Scrape lot related data from wholesaler website. 
- Analyze items in the lot. 
- Get median sold prices per each item from Ebay via API. 
- Sum up median prices from Ebay and write results to Excel for further analysis. 

##### Python packages used :
1. os  - for working with OS
2. requests, BeautifulSoup, re - for parsing and working with HTTP requests
3. openpyxl - for working with Excel files
4. sqlite3 - light database for storing some info
5. json - for handling API responses
