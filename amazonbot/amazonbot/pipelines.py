# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from os import link
from itemadapter import ItemAdapter
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from scrapy.exceptions import DropItem
import time


class AmazonbotPipeline:
    def process_item(self, item, spider):
        return item


class AmazonbotSellersRankFilterPipeline:
    def process_item(self, item, spider):
        asin = item['asin']
        total_tr_price = item['total_tr_price']
        total_us_price = item['total_us_price']
        us_sellers_rank = item['us_sellers_rank']
        if not us_sellers_rank or us_sellers_rank > spider.max_sellers_rank:
            raise DropItem(f"DROPPED - ASIN: {asin} - Sellers rank is not defined or not below {spider.max_sellers_rank}")
        else:
            return {
                "asin": asin,
                "total_tr_price": total_tr_price,
                "total_us_price": total_us_price,
                "us_sellers_rank": us_sellers_rank
            }


class AmazonbotFBAProfitabilityFilterPipeline:
    INCH_TO_CM = 2.54
    USD_TO_TRY = 8.5
    POUND_TO_KG = 0.4535923
    AIR_COST_PER_W = 7 # Cost per weight as USD
    SEA_COST_PER_W = 3 # Cost per weight as USD
    FBA_SELLING_FEE_RATE = 0.15
    MINIMUM_ALLOWED_NET_PROFIT = -2 # as USD
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.fba_calculator_url = "https://sellercentral.amazon.com/hz/fba/profitabilitycalculator/index?lang=en_US"

    def process_item(self, item, spider):
        asin = item['asin']
        total_tr_price = item['total_tr_price']
        if not total_tr_price:
            raise DropItem(f"DROPPED - ASIN: {asin} - Missing total_tr_price")
        total_us_price = item['total_us_price']
        if not total_us_price:
            raise DropItem(f"DROPPED - ASIN: {asin} - Missing total_us_price")
        us_sellers_rank = item['us_sellers_rank']
        self.driver.get(self.fba_calculator_url)
        time.sleep(5)
        # If link continue popup occurs, click that
        try_count = 0
        while try_count < 5:
            link_continue = self.driver.find_elements_by_xpath("//*[@id='link_continue']")
            if link_continue:
                link_continue[0].click()
                time.sleep(5)
                break
            try_count += 1
            time.sleep(3)
        # Enter asin
        search_string = self.driver.find_element_by_xpath("//*[@id='search-string']")
        for s in asin:
            search_string.send_keys(s)
            time.sleep(0.5)
        search_string.send_keys(Keys.ENTER)
        time.sleep(5)
        # Product dimensions and weight
        product_length = float(self.driver.find_element_by_xpath("//*[@id='product-info-length']").text)
        product_width = float(self.driver.find_element_by_xpath("//*[@id='product-info-width']").text)
        product_height = float(self.driver.find_element_by_xpath("//*[@id='product-info-height']").text)
        dimensional_weight = (product_length * self.INCH_TO_CM) * (product_width * self.INCH_TO_CM) * (product_height * self.INCH_TO_CM) / 5000
        product_weight = float(self.driver.find_element_by_xpath("//*[@id='product-info-weight']").text)
        max_product_weight = max(dimensional_weight, product_weight)
        # Product revenue
        revenue = total_us_price # Revenue thought as minimum of the us sellers prices
        # Click Calculate button to see fulfillment fee
        self.driver.find_element_by_xpath("//*[@id='update-fees-link-announce']").click()
        time.sleep(5)
        # Fees
        fba_fulfillment_fee = float(self.driver.find_element_by_xpath("//*[@id='afn-amazon-fulfillment-fees']").text)
        air_ship_to_amazon_cost = self.AIR_COST_PER_W * max_product_weight
        sea_ship_to_amazon_cost = self.SEA_COST_PER_W * max_product_weight
        fba_charge = max(0.3, total_us_price*self.FBA_SELLING_FEE_RATE)
        air_total_fulfillment_cost = air_ship_to_amazon_cost + fba_charge
        sea_total_fulfillment_cost = sea_ship_to_amazon_cost + fba_charge
        # Storage cost
        storage_cost = 0
        # Product cost
        product_cost = total_tr_price / self.USD_TO_TRY
        # Calculate Profitability
        air_net_profit = revenue - fba_fulfillment_fee - air_total_fulfillment_cost - storage_cost - product_cost
        sea_net_profit = revenue - fba_fulfillment_fee - sea_total_fulfillment_cost - storage_cost - product_cost
        air_roi = round(air_net_profit / (air_ship_to_amazon_cost+product_cost),2)
        sea_roi = round(sea_net_profit / (sea_ship_to_amazon_cost+product_cost),2)
        if air_net_profit > self.MINIMUM_ALLOWED_NET_PROFIT:
            return {
                "asin": asin,
                "total_tr_price": total_tr_price,
                "total_us_price": total_us_price,
                "us_sellers_rank": us_sellers_rank,
                "net_profit": air_net_profit,
                "roi": air_roi,
                "profitable_with": 'AIR_SHIPPING'
            }
        elif sea_net_profit > self.MINIMUM_ALLOWED_NET_PROFIT:
            return {
                "asin": asin,
                "total_tr_price": total_tr_price,
                "total_us_price": total_us_price,
                "us_sellers_rank": us_sellers_rank,
                "net_profit": sea_net_profit,
                "roi": sea_roi,
                "profitable_with": 'SEA_SHIPPING'
            }
        else:
            raise DropItem(f"DROPPED - ASIN: {asin} - Product is not profitable, Air Net Profit: {air_net_profit}, Sea Net Profit: {sea_net_profit}")