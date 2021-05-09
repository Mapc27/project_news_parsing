import datetime

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import BG_URL
import unicodedata


class BusinessGazetaSpider(scrapy.Spider):
    name = 'BusinessGazeta'
    start_urls = ['https://www.business-gazeta.ru/news']
    url = BG_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.completed = False
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.article-news__desc')[1:]:

            href = news.css('a::attr(href)').extract_first()
            n = href.rfind('/')
            href = href[n:]

            yield response.follow(self.start_urls[0] + href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page+1), callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('time.article__date::attr(datetime)').extract_first()
        published_date = datetime.datetime.strptime(published_date, "%Y-%m-%dMSK%H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('h1.article__h1::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.articleBody').css('p ::text').extract()).replace(u'\r', u'').replace(u'\n', u'')
        text = unicodedata.normalize("NFKD", text)

        dictionary = {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }
        yield dictionary


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(BusinessGazetaSpider,
                  limit_published_date=datetime.datetime(2021, 5, 6, 17, 56))
    process.start()
