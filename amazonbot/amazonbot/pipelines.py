# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class AmazonbotPipeline:
    def process_item(self, item, spider):
        return item


class AmazonbotSoldByAmazonFilterPipeline:
    def process_item(self, item, spider):
        amazon_seller_name = "Amazon"
        if item['seller']:
            if amazon_seller_name.lower() in item['seller'].lower():
                raise Exception(f"Not a product sold by Amazon - Seller Name: {item['seller']}")
            return item
        else:
            raise Exception(f"Missing seller name in {item}")
        return item
