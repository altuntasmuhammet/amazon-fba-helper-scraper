import scrapy
from scrapy_selenium import SeleniumRequest
import time
from datetime import datetime
import urllib.parse
import logging

from amazonbot import utils
from amazonbot import helpers


KEYWORD = "kalem"


class AmazontrSpider(scrapy.Spider):
    name = 'amazontr'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2840.71 Safari/539.36'}
    allowed_domains = ['amazon.com.tr', 'amazon.com']
    count = 0
    COUNT_MAX = float('inf')
    # start_urls = ['http://amazon.com.tr/']

    def __init__(self, keywords="", url="", min_page=1, max_page=200, max_sellers_rank=100000, *args, **kwargs):
        super(AmazontrSpider, self).__init__(*args, **kwargs)
        self.keywords = [k.strip() for k in keywords.split(",") if k.strip()]
        self.url = url
        self.min_page = int(min_page)
        self.max_page = int(max_page)
        self.max_sellers_rank = int(max_sellers_rank)
        self._looked_products = []

    def start_requests(self):
        if self.keywords:
            title_query_url_template = "https://www.amazon.com.tr/s?k={keyword}&page={page}"
            for keyword in self.keywords:
                encoded_keyword = urllib.parse.quote(keyword)
                for page in range(self.min_page, self.max_page+1):
                    url = title_query_url_template.format(
                        keyword=encoded_keyword, page=page)
                    # yield scrapy.Request(url=url, callback=self.parse_products, headers=self.headers)
                    yield SeleniumRequest(url=url, callback=self.parse_products)
        if self.url:
            params = {}
            for page in range(self.min_page, self.max_page):
                params["page"] = page
                url = helpers.update_url_query(self.url, params)
                yield SeleniumRequest(url=url, callback=self.parse_products)

    def parse_products(self, response):
        products = response.xpath("//div[starts-with(@data-asin,'B0')]")
        # product_url_template = "https://www.amazon.com.tr/dp/{asin}"
        product_url_template = "https://www.amazon.com.tr/gp/aod/ajax/ref=aod_f_used?asin={asin}&m=&pinnedofferhash=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&pageno=1&filters={{%22new%22:true}}"
        for product in products:
            asin = product.attrib['data-asin'].strip()
            url = product_url_template.format(asin=asin)
            print("product_url:", url)
            logging.info("product_url:" + url)
            self.count += 1
            if self.count < self.COUNT_MAX:
                yield SeleniumRequest(url=url, callback=self.parse_tr_product_data, meta={'asin': asin})

    def parse_tr_product_data(self, response):
        asin = response.meta.get('asin', None)
        logging.info(str('tabular-buybox-container' in str(response.body)))
        # parse buybox seller name
        sold_by_elements = response.xpath("//*[@id='aod-offer-soldBy']")
        if sold_by_elements:
            texts = [text for text in sold_by_elements[0].xpath(
                ".//text()").extract() if text.strip()]
            seller_name = texts[1]
        else:
            seller_name = ""
        # parse prices
        prices = utils.get_lowest_product_prices_from_sellers_page(response)
        if 'amazon' in seller_name.lower():
            product_url_template = "https://www.amazon.com/dp/{asin}"
            # product_url_template = "https://www.amazon.com/gp/aod/ajax/ref=aod_f_used?asin={asin}&m=&pinnedofferhash=&qid=&smid=&sourcecustomerorglistid=&sourcecustomerorglistitemid=&sr=&pc=dp&pageno=1&filters={%22new%22:true}"
            url = product_url_template.format(asin=asin)
            meta = {
                "asin": asin,
                "total_tr_price": prices[0] + prices[1] if prices else None
            }
            yield SeleniumRequest(url=url, callback=self.parse_us_product_data, meta=meta)

    def parse_us_product_data(self, response):
        asin = response.meta.get("asin")
        total_tr_price = response.meta.get("total_tr_price")
        # Check if product exists in US
        if response.status == 200:
            sorryDiv = response.xpath(
                "//img[contains(@alt,'Sorry! We could')]")
            if sorryDiv:
                return None
        # Parse product prices
        prices = utils.get_product_prices_from_product_page(response)
        total_us_price = prices[0] + prices[1] if prices else None
        # Parse sellers rank
        us_sellers_rank = utils.get_sellers_rank(response)
        yield {
            "asin": asin,
            "total_tr_price": total_tr_price,
            "total_us_price": total_us_price,
            "us_sellers_rank": us_sellers_rank
        }
