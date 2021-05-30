# -*- coding: utf-8 -*-
import datetime
import json

from scrapy.crawler import CrawlerProcess
from multiprocessing import Pool
from scrapy.utils.serialize import ScrapyJSONEncoder



from news.spiders.BusinessGazeta import BusinessGazetaSpider
from news.spiders.EveningKazan import EveningKazanSpider
from news.spiders.InKazan import InKazanSpider
from news.spiders.KazanFirst import KazanFirstSpider
from news.spiders.ProKazan import ProKazanSpider
from news.spiders.RealnoeVremya import RealnoeVremyaSpider
from news.spiders.TatarInform import TatarInformSpider
from news.spiders.Tatarstan24 import Tatarstan24Spider
from news.spiders.TNV import TNVSpider
from news.spiders.Match import MatchSpider

last_datetime_scraping = datetime.datetime.now() - datetime.timedelta(hours=2)

spiders_list = [
    TatarInformSpider,
    BusinessGazetaSpider,
    EveningKazanSpider,
    InKazanSpider,
    KazanFirstSpider,
    ProKazanSpider,
    RealnoeVremyaSpider,
    Tatarstan24Spider,
    TNVSpider,
]


class CustomCrawler:
    def __init__(self, limit):
        self.output = {}
        self.process = CrawlerProcess(settings={'LOG_ENABLED': False})
        self.limit = limit

    def yield_output(self, data):
        self.output[data[0]['from_site']] = data

    def crawl(self, cls):
        self.process.crawl(cls, callback=self.yield_output, limit_published_date=self.limit)


def crawl_static(list_of_cls, limit):
    crawler = CustomCrawler(limit)
    for cls in list_of_cls:
        crawler.crawl(cls)
    crawler.process.start()
    return crawler.output


class Matching:
    def __init__(self):
        self.output = []
        self.process = CrawlerProcess(settings={'LOG_ENABLED': False})

    def yield_output(self, data):
        self.output.append(data)

    def crawl(self, cls, lst):
        self.process.crawl(cls, callback=self.yield_output, news_lst=lst)


def crawl_match(data):
    crawler = Matching()

    for site in data:
        if site == 'TatarInform':
            continue
        for other_news in data[site]:
            news_lst = []
            for ti_news in data['TatarInform']:
                news_lst.append([other_news, ti_news])
            crawler.crawl(MatchSpider, news_lst)

    crawler.process.start()

    return crawler.output


def main(limit):
    out = crawl_static(spiders_list, limit)

    return out


if __name__ == '__main__':
    lmt = datetime.datetime.now()-datetime.timedelta(hours=2)
    data_ = main(lmt)
    for site in data_:
        print('=' * 50, site, '=' * 50)
        for news in data_[site]:
            print('\t', news)
    # тут могла быть ваша БД
    # data_['TatarInform'].append(get_ti_news())

    result = Pool(1).map(crawl_match, (data_,))[0]

    for i in range(len(data_['TatarInform'])):
        result.append(data_['TatarInform'][i])
    for i in result:
        print(i)
