from scrapy import Selector
import re
from .helpers import extract_integer


def get_sellers_rank(response):
    seller_rank_pattern = r'([0-9]{1,3}(?:,[0-9]{0,3})*)\s(?:in|en)\s([a-zA-Z]{3,})'
    best_seller_link_pattern = r'gp/bestsellers/'
    sellers_ranks = []
    conditions = [
                  "@id='detail-bullets'",
                  "@id='productDetailsTable'",
                  "@id='descriptionAndDetails'",
                  "@id='prodDetails'",
                  "@id='prodDetails' and @class='a-section'",
                  "@id='detailBullets_feature_div'"
                ]
    sel = Selector(response)
    for condition in conditions:
        prod_detail_elements = sel.xpath(f"//*[{condition}]")
        if prod_detail_elements:
            best_seller_link_elements = prod_detail_elements[0].xpath('.//span').get()
            if best_seller_link_elements:
                prod_detail = prod_detail_elements[0].get()
                prod_detail = prod_detail.replace("\n", " ")
                x = re.search(seller_rank_pattern, prod_detail)
                if x:
                    sellers_rank = extract_integer(x.group().replace(',', ''))
                    return sellers_rank
