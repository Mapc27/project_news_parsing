import datetime
import time

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
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

import db


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


# служебная функция
def find_max_id(list_ti_news):
    if list_ti_news[-1]['id'] == len(list_ti_news) - 1:
        current_id = 0
        for ti_news in list_ti_news:
            if ti_news['id'] > current_id:
                current_id = ti_news['id']
    else:
        current_id = list_ti_news[-1]['id'] + 1
    return current_id


class Parse:
    """
    all_news = news scraped from all news spiders (without MatchSpider)
    ti_news = news scraped from TatarInformParser
    other_news = all_news без ti_news
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

        self.runner = CrawlerRunner(get_project_settings())  # из названия понятно

    def store_news(self, data):
        # служебный метод
        # callback для спарсенных новостей
        # вызывается для каждого паука (сайта)
        if data:
            self.scraped_news[data[0]['from_site']] = data

    def store_result(self, data):
        # служебный метод
        # callback для результата
        # вызывается для каждой other_news
        self.result.append(data)

    def print_end(self):
        print('#' * 500)
        print('#' * 500)
        print('=' * 20, '[Свободная касса]', '=' * 20)
        print('#' * 500)
        print('#' * 500)
        print('=' * 20, '[Ожидаю {} секунд ...]'.format(self.timeout), '=' * 20)
        print()
        print()
        print()
        time.sleep(self.timeout)

    @defer.inlineCallbacks  # хз, что он делает
    def run_process(self):
        while True:
            # обновляем хранилища
            self.result = []
            self.scraped_news = {}

            print('=' * 30, '[Скребок запущен]', '=' * 30)
            print('=' * 20, '[datetime scraping]', '=' * 10, '[', self.limit.__str__(), ']', '=' * 20)

            # сбор новостей
            print('=' * 30, '[Собираю новости ...]', '=' * 30)
            for spider in spiders_list:
                yield self.runner.crawl(spider, callback=self.store_news, limit_published_date=self.limit)

            print('=' * 30, '[Новости собраны]', '=' * 30)
            # изменяем, чтобы парсить только свежие новости
            self.limit = datetime.datetime.now()

            # вывод на экран
            all_news_count = 0
            for site in self.scraped_news:
                print('=' * 50, site, '=' * 50)
                for ti_news in self.scraped_news[site]:
                    all_news_count += 1
                    print('\t' * 2, ti_news)

            if all_news_count == 0:
                print('=' * 30, '[Новостей нет]', '=' * 30)
                self.print_end()
                continue

            try:
                len_ti = len(self.scraped_news['TatarInform'])
            except KeyError:
                self.scraped_news['TatarInform'] = []
                len_ti = 0

            print('len(all) = ', all_news_count)
            print('len(TI) = ', len_ti)
            print('=' * 100)
            print('=' * 100)

            print('=' * 20, '[Достаю ТИ новости с БД ...]', '=' * 20)

            # достаём ti_news c БД
            list_ti_news = db.get_all_ti_news()

            print('=' * 20, '[Успешно достал ТИ новости с БД ...]', '=' * 20)

            if list_ti_news:
                # ищем максимальный id ти новостей с БД
                current_id = find_max_id(list_ti_news)
            else:
                current_id = 1

            # проставляем id
            for ti_news in self.scraped_news['TatarInform']:
                ti_news['id'] = current_id
                current_id += 1

            # if other_news == None
            if len_ti == all_news_count:
                print('=' * 20, '[Нет новых новостей]', '=' * 20)
                print('=' * 20, '[Добавляю, всё что есть в БД ...]', '=' * 20)

                # добаляем self.scraped_news['TatarInform'] в БД
                db.add_ti_news_list(self.scraped_news['TatarInform'])

                self.print_end()
                continue

            # собираю всё в кучу
            list_ti_news += self.scraped_news['TatarInform']

            print('=' * 20, '[Отправляю запросы на сравнение новостей ...]', '=' * 20)

            # отправляем запросы MatchSpider
            # если коротко, то берём каждую other_news и в пару к ней все ti_news
            # [[other_news, ti_news_1], [other_news, ti_news_2], [other_news, ti_news_3], ...]
            for site in self.scraped_news:
                if site == 'TatarInform':
                    continue
                for other_news in self.scraped_news[site]:
                    news_lst = []
                    for ti_news in list_ti_news:
                        news_lst.append([other_news, ti_news])

                    yield self.runner.crawl(MatchSpider, news_lst=news_lst, callback=self.store_result)

            # считаю количество новостей, которые совпали с одной из ти новости
            true_news_count = 0
            for news in self.result:
                if news['is_match']:
                    true_news_count += 1

            # добавляем result в БД
            print('=' * 20, '[Добавляю competition news в БД ...]', '=' * 20)
            db.add_comp_news_list(self.result)

            # добавляем TI news в БД
            print('=' * 20, '[Добавляю новости с ТатарИнформ в БД ...]', '=' * 20)
            db.add_ti_news_list(self.scraped_news['TatarInform'])

            # Вывод result
            print('=' * 20, 'result', '=' * 20)
            print('true_news_count = ', true_news_count)
            print('len(self.result) = ', len(self.result))
            for news in self.result:
                print('-' * 5, '[',  news['is_match'], ']', '-' * 5, news)

            # вывод ти новостей
            print('#' * 500)
            for ti_news in list_ti_news:
                print('-' * 5, '[',  ti_news['id'], ']', '-' * 5, ti_news)

            self.print_end()

            time.sleep(self.timeout)

        reactor.stop()


if __name__ == '__main__':
    configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
    initial_limit = datetime.datetime.now() - datetime.timedelta(minutes=30)

    parser = Parse(limit=initial_limit)
    parser.run_process()

    reactor.run()
