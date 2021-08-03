# amazon-scraper-usecase-1
## Description
It is a code for obtaining products which are:
- sold by Amazon in amazon.com.tr
- sellers rank's are below defined limit in the US({max_sellers_rank})
by searching keywords

## Requirements
Python>=3.6.x
ChromeDriver (https://chromedriver.chromium.org/)

## Create virtual environment
```sh
python3 -m venv env
```
## Install dependencies
```sh
pip install -r requirements.txt
```
## Run
```sh
cd amazonbot
scrapy crawl amazontr -a keywords="boya kalemi" -a min_page=1 -a max_page=1 max_sellers_rank=100000 -o boya-kalemi.json
```