# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter

import news.source.match as match


class NewsPipeline:
    def __init__(self):
        self.lst = []

    def process_item(self, item, spider):
        self.lst.append(item)

    def close_spider(self, spider):
        pass

