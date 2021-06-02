# -*- coding: utf-8 -*-
import datetime
import time


from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor, defer


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


class Parse:
    """
    all_news = news scraped from all news spiders (without MatchSpider)
    ti_news = news scraped from TatarInformParser
    other_news = all_news \ ti_news
    """
    def __init__(self, limit, timeout=30):
        """
        :param limit: initial state when parsing was done
        :param timeout: timeout between iteration
        """
        self.timeout = timeout
        self.limit = limit
        self.scraped_news = {}  # хранилище для спарсенных новостей
        self.result = []  # хранилище для результата

        self.runner = CrawlerRunner()  # из названия понятно

    def store_news(self, data):
        # служебный метод
        # callback для спарсенных новостей
        # вызывается для каждого паука (сайта)
        self.scraped_news[data[0]['from_site']] = data

    def store_result(self, data):
        # служебный метод
        # callback для результата
        # вызывается для каждой other_news
        self.result.append(data)

    @defer.inlineCallbacks  # хз, что он делает
    def run_process(self):
        while True:
            print('=' * 20, '[datetime scraping]', '=' * 10, self.limit.__str__(), '=' * 20)

            # сбор новостей
            for spider in spiders_list:
                yield self.runner.crawl(spider, callback=self.store_news, limit_published_date=self.limit)

            # изменяем, чтобы парсить только свежие новости
            self.limit = datetime.datetime.now()

            # вывод на экран
            all_news_count = 0
            for site in self.scraped_news:
                print('=' * 50, site, '=' * 50)
                for ti_news in self.scraped_news[site]:
                    all_news_count += 1
                    print('-' * 10, ti_news)

            len_ti = len(self.scraped_news['TatarInform'])

            print('len(all) = ', all_news_count)
            print('len(TI) = ', len_ti)
            print('=' * 100)
            print('=' * 100)

            # other_news = None
            if len_ti == all_news_count:
                # добаляем self.scraped_news['TatarInform'] в БД
                time.sleep(self.timeout)
                continue

            # достаём ti_news c БД
            # ti_news_list =

            # отправляем запросы MatchSpider
            # если коротко, то берём каждую other_news и в пару к ней все ti_news
            # [[other_news, ti_news_1], [other_news, ti_news_2], [other_news, ti_news_3], ...]
            for site in self.scraped_news:
                if site == 'TatarInform':
                    continue
                for other_news in self.scraped_news[site]:
                    news_lst = []
                    for ti_news in self.scraped_news['TatarInform']:
                        news_lst.append([other_news, ti_news])

                    yield self.runner.crawl(MatchSpider, news_lst=news_lst, callback=self.store_result)

            true_news_count = 0
            for news in self.result:
                if news['is_match'] == 'True':
                    true_news_count += 1

            # дабавляем в result ti_news, так как MatchSpider возвращает только other_news
            for ti_news in self.scraped_news['TatarInform']:
                self.result.append(ti_news)

            # добавляем result в БД

            # Вывод result
            print('&' * 20, 'result', '&' * 20)
            print('true_news_count = ', true_news_count)
            print('len(self.result) = ', len(self.result))
            for news in self.result:
                print('-' * 10, news)

            # обновляем хранилища
            self.result = []
            self.scraped_news = {}

            print('#' * 500)
            print('#' * 500)
            print('#' * 500)
            print('#' * 500)
            print('#' * 500)
            print()

            time.sleep(self.timeout)

        reactor.stop()


if __name__ == '__main__':
    initial_limit = datetime.datetime.now() - datetime.timedelta(minutes=30)

    parser = Parse(limit=initial_limit)
    parser.run_process()

    reactor.run()
