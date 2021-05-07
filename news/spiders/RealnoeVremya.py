import datetime

import scrapy
from config import RV_URL
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class RealnoeVremyaSpider(scrapy.Spider):
    name = 'RealnoeVremya'
    start_urls = ['https://realnoevremya.ru']
    url = RV_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.completed = False
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('li.withPic'):

            href = news.css('a::attr(href)').extract_first()

            yield response.follow(self.start_urls[0] + href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            next_page = response.css('div.headerBlock').css('span.nowrap').css('a::attr(href)').extract_first()

            yield response.follow(self.start_urls[0] + next_page, callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('div.dateLine').css('a::text').extract_first().strip()
        published_date = datetime.datetime.strptime(published_date, "%H:%M, %d.%m.%Y")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('div.detailCont').css('h1::text').extract_first().strip().replace(u'\xa0', u' ')

        href = response.url

        text = ' '.join(response.css('div.detailCont').css('p ::text').extract()).replace(u'\xa0', u' ')

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(RealnoeVremyaSpider,
                  limit_published_date=datetime.datetime(2021, 5, 3, 21, 4))
    process.start()
