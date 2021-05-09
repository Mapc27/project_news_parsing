# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime

from itemadapter import ItemAdapter


class NewsPipeline:
    def __init__(self):
        self.lst = []

    def process_item(self, item, spider):
        self.lst.append(item)
        return item

    def close_spider(self, spider):
        for i in range(len(self.lst)-1):
            for j in range(i, len(self.lst)):
                if datetime.datetime.strptime(self.lst[i]['published_date'], "%Y-%m-%d %H:%M:%S") <\
                        datetime.datetime.strptime(self.lst[j]['published_date'], "%Y-%m-%d %H:%M:%S"):
                    self.lst[i],  self.lst[j] = self.lst[j], self.lst[i]
        for i in self.lst:
            print(i)
