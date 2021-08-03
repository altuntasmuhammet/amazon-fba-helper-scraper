import scrapy
from scrapy_selenium import SeleniumRequest
import time
from datetime import datetime
import urllib.parse
import logging


KEYWORD = "kalem"


class AmazontrSpider(scrapy.Spider):
    name = 'amazontr'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2840.71 Safari/539.36'}
    allowed_domains = ['amazon.com.tr', 'amazon.com']
    # start_urls = ['http://amazon.com.tr/']

    def __init__(self, keywords="", min_page=1, max_page=200, *args, **kwargs):
        super(AmazontrSpider, self).__init__(*args, **kwargs)
        self.keywords = [k.strip() for k in keywords.split(",")]
        self.min_page = int(min_page)
        self.max_page = int(max_page)
        self._looked_products = []

    def start_requests(self):
        title_query_url_template = "https://www.amazon.com.tr/s?k={keyword}&page={page}"
        for keyword in self.keywords:
            encoded_keyword = urllib.parse.quote(keyword)
            for page in range(self.min_page, self.max_page+1):
                url = title_query_url_template.format(
                    keyword=encoded_keyword, page=page)
                # yield scrapy.Request(url=url, callback=self.parse_products, headers=self.headers)
                yield SeleniumRequest(url=url, callback=self.parse_products)

    def parse_products(self, response):
        products = response.xpath("//div[starts-with(@data-asin,'B0')]")
        product_url_template = "https://www.amazon.com.tr/dp/{asin}"
        for product in products:
            asin = product.attrib['data-asin'].strip()
            url = product_url_template.format(asin=asin)
            print("product_url:", url)
            logging.info("product_url:" + url)
            yield SeleniumRequest(url=url, callback=self.parse_tr_product_data, meta={'asin': asin})

    def parse_tr_product_data(self, response):
        asin = response.meta.get('asin', None)
        logging.info(str('tabular-buybox-container' in str(response.body)))
        with open('onefile.txt', 'wb') as f:
            f.write(response.body)
        buybox_column_text = response.xpath(
            "//*[@class='tabular-buybox-text']/text()").get()
        if buybox_column_text:
            print("BUYBOX_COLUM_TEXT:", buybox_column_text)
            logging.info("BUYBOX_COLUM_TEXT:" + buybox_column_text)
            seller_name = buybox_column_text.strip()
            print("************************" " SELLER_NAME: ",
                  seller_name, "************************")
            if 'amazon' in seller_name.lower():
                url = f"https://www.amazon.com/dp/{asin}"
                yield SeleniumRequest(url=url, callback=self.parse_us_product_data, meta={'asin': asin})
        else:
            print("************************" " SELLER_NAME: ",
                  None, "************************")

    def parse_us_product_data(self, response):
        asin = response.meta.get('asin')
        if response.status == 200:
            sorryDiv = response.xpath("//img[contains(@alt,'Sorry! We could')]")
            if not sorryDiv:
                yield {
                    "asin": asin
                }
