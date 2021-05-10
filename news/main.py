import datetime
import os

from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from news.spiders.BusinessGazeta import BusinessGazetaSpider
from news.spiders.EveningKazan import EveningKazanSpider
from news.spiders.InKazan import InKazanSpider
from news.spiders.KazanFirst import KazanFirstSpider
from news.spiders.ProKazan import ProKazanSpider
from news.spiders.RealnoeVremya import RealnoeVremyaSpider
from news.spiders.TatarInform import TatarInformSpider
from news.spiders.Tatarstan24 import Tatarstan24Spider
from news.spiders.TNV import TNVSpider


# словарь с datetime последних scraped news для каждого сайта
dict_of_last_published_dates = {
    'BusinessGazetaSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'EveningKazanSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'InKazanSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'KazanFirstSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'ProKazanSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'RealnoeVremyaSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'TatarInformSpider': datetime.datetime(2021, 5, 9, 21, 4),
    'Tatarstan24Spider': datetime.datetime(2021, 5, 9, 21, 4),
    'TNVSpider': datetime.datetime(2021, 5, 9, 21, 4),
    }


def main():
    pass


if __name__ == '__main__':
    # этот код взял с форума, так как этот файл main.py не может получить settings
    # поэтому settings получаются так, а не через get_project_settings(), как это можно было сделать в пауках
    settings = Settings()
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'news.settings'
    settings_module_path = os.environ['SCRAPY_SETTINGS_MODULE']
    settings.setmodule(settings_module_path, priority='project')

    process = CrawlerProcess(settings)

    process.crawl(BusinessGazetaSpider,
                  limit_published_date=dict_of_last_published_dates['BusinessGazetaSpider'])
    process.crawl(EveningKazanSpider,
                  limit_published_date=dict_of_last_published_dates['EveningKazanSpider'])
    process.crawl(InKazanSpider,
                  limit_published_date=dict_of_last_published_dates['InKazanSpider'])
    process.crawl(KazanFirstSpider,
                  limit_published_date=dict_of_last_published_dates['KazanFirstSpider'])
    process.crawl(ProKazanSpider,
                  limit_published_date=dict_of_last_published_dates['ProKazanSpider'])
    process.crawl(RealnoeVremyaSpider,
                  limit_published_date=dict_of_last_published_dates['RealnoeVremyaSpider'])
    process.crawl(TatarInformSpider,
                  limit_published_date=dict_of_last_published_dates['TatarInformSpider'])
    process.crawl(Tatarstan24Spider,
                  limit_published_date=dict_of_last_published_dates['Tatarstan24Spider'])
    process.crawl(TNVSpider,
                  limit_published_date=dict_of_last_published_dates['TNVSpider'])

    process.start()
