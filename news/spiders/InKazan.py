import datetime
import json
import unicodedata

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import IK_URL


class InKazanSpider(scrapy.Spider):
    name = 'InKazan'
    start_urls = ['https://inkazan.ru']
    url = IK_URL
    min_date: datetime.datetime

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        now = datetime.datetime.now()
        yield scrapy.Request(self.url.format(date_time=now.date().__str__() + 'T'
                                                       + now.time().__str__()), callback=self.parse)

    def parse(self, response, **kwargs):
        published_at = datetime.datetime.now()
        for news in json.loads(response.text):
            href = self.start_urls[0] + news['site_path']

            published_at = news['published_at']['iso']
            n = published_at.rfind('.')
            published_at = published_at[:n]
            published_at = datetime.datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%S")

            yield response.follow(href, callback=self.parse_news, cb_kwargs={'published_date': published_at})

            if self.completed:
                break

        self.min_date = published_at

        if not self.completed:
            yield response.follow(self.url.format(date_time=published_at.date().__str__() + 'T'
                                                            + published_at.time().__str__()), callback=self.parse)

    def parse_news(self, response, **kwargs):
        published_date = kwargs.get('published_date', None)

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('div.title::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.content-blocks').css('p ::text')
                        .extract()).strip().replace(u'\r', u'').replace(u'\n', u'')
        text = unicodedata.normalize("NFKD", text)

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(InKazanSpider,
                  limit_published_date=datetime.datetime(2021, 5, 3, 21, 4))
    process.start()
