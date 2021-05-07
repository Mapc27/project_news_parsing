import datetime

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import months_names, TI_URL


class TatarInformSpider(scrapy.Spider):
    name = 'TatarInform'
    start_urls = ['https://www.tatar-inform.ru/news/widget/list/novosti/page/']
    url = TI_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.completed = False

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('li.underline-list__item'):

            href = news.css('div.list-item__content').css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page+1), callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('div.page-main__publish-data').css('a::text').extract_first().strip()
        published_date = published_date.replace(u'\xa0\xa0', u' ')

        month = published_date.split(' ')[1]
        replace = months_names.index(month)

        published_date = published_date.replace(month, str(replace))
        published_date = datetime.datetime.strptime(published_date, "%d %m %Y %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('h1.page-main__title::text').extract_first().strip().replace(u'\xa0', u' ')

        href = response.url

        text = ' '.join(response.css('div.page-main__text').css('p ::text').extract()).strip().replace(u'\xa0', u' ')

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(TatarInformSpider,
                  limit_published_date=datetime.datetime(2021, 5, 3, 21, 4))
    process.start()
