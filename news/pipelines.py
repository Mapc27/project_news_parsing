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
        # сюда попадает каждая новость с паука в item
        # нужно добавить метод добавления новости в БД
        self.lst.append(item)

    def close_spider(self, spider):
        if spider.name == 'TatarInform':
            match.ti_array = self.lst
        else:
            for i in self.lst:
                match.other_array.append(i)

