# amazon-scraper-usecase-1
## Description
It is a code for obtaining products which are:
- sold by Amazon in amazon.com.tr
- sellers rank's are below defined limit in the US({max_sellers_rank})
by searching keywords

## Requirements
- Python>=3.6.x
- ChromeDriver (https://chromedriver.chromium.org/)

## Install dependencies
```sh
pip install -r requirements.txt
```

## Run
By keyword
```sh
cd amazonbot
scrapy crawl amazontr -a keywords="boya kalemi, cetvel" -a min_page=1 -a max_page=1 -a max_sellers_rank=100000 -o boya-kalemi.json --logfile my_log.log --loglevel INFO
```
By URL
```sh
cd amazonbot
scrapy crawl amazontr -a url=<AMAZON_URL> -a min_page=1 -a max_page=1 -a max_sellers_rank=100000 -o boya-kalemi.json --logfile my_log.log --loglevel INFO
```

## Notes
For Linux/Mac OS users
chromedriver.exe must be placed in /usr/local/bin or /usr/local/bin path.
For Windows user
chromedriver.exe path must be defined using SELENIUM_DRIVER_EXECUTABLE_PATH in amazonbot/amazonbot/settings
SELENIUM_DRIVER_EXECUTABLE_PATH = "path\\to\\<chromedriver.exe"