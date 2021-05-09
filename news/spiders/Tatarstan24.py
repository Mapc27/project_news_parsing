import datetime
import unicodedata

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import T2_URL


class Tatarstan24Spider(scrapy.Spider):
    name = 'Tatarstan24'
    start_urls = ['https://tatarstan24.tv/']
    url = T2_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('a.media-list__head'):

            href = news.css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('a.page-main__publish__date::text').extract_first().strip()

        published_date = datetime.datetime.strptime(published_date, "%H:%M %d.%m.%Y")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('h1.page-main__head::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.page-main__text').css('p ::text')
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
    process.crawl(Tatarstan24Spider,
                  limit_published_date=datetime.datetime(2021, 5, 3, 21, 4))
    process.start()
