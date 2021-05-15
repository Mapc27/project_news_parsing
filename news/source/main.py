import datetime

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from news.spiders.BusinessGazeta import BusinessGazetaSpider
from news.spiders.EveningKazan import EveningKazanSpider
from news.spiders.InKazan import InKazanSpider
from news.spiders.KazanFirst import KazanFirstSpider
from news.spiders.ProKazan import ProKazanSpider
from news.spiders.RealnoeVremya import RealnoeVremyaSpider
from news.spiders.TatarInform import TatarInformSpider
from news.spiders.Tatarstan24 import Tatarstan24Spider
from news.spiders.TNV import TNVSpider


last_datetime_scraping = datetime.datetime.now() - datetime.timedelta(hours=1)


def main():
    pass


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())

    process.crawl(BusinessGazetaSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(EveningKazanSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(InKazanSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(KazanFirstSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(ProKazanSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(RealnoeVremyaSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(TatarInformSpider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(Tatarstan24Spider,
                  limit_published_date=last_datetime_scraping)
    process.crawl(TNVSpider,
                  limit_published_date=last_datetime_scraping)
    process.start()
