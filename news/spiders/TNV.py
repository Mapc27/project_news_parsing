import datetime
import unicodedata

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import TNV_URL, months_names


not_needed = ['Читайте также', 'Фото:', 'Видео', 'Автор']


class TNVSpider(scrapy.Spider):
    name = 'TNV'
    start_urls = ['https://tnv.ru']
    url = TNV_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.news-page-list__item'):

            href = news.css('a::attr(href)').extract_first()
            href = self.start_urls[0] + href

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("=")[-1])
            yield response.follow(self.url + str(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        try:
            published_date = response.css('div.novelty__information').css('p.novelty__date::text').extract_first().strip()
        except AttributeError:
            return response.follow(response.url, callback=self.parse)
        month = published_date.split(' ')[1]
        replace = months_names.index(month.lower())

        published_date = published_date.replace(month, str(replace))
        published_date = datetime.datetime.strptime(published_date, "%d %m %Y, %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('div.page__head').css('h1::text') \
            .extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        array = response.css('div.js-image-description ::text').extract()

        # for i in range(len(array)):
        #     for j in not_needed:
        #         if j in array[i] or j.lower() in array[i]:
        #             array[i] = ''

        text = ' '.join(array).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
        text = unicodedata.normalize("NFKD", text)

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }


if __name__ == '__main__':
    # создаём process
    # get_project_settings() передаёт settings в том числе файл pipeline.py, в который уходят данные с парсинга
    process = CrawlerProcess(get_project_settings())
    # переда1м параметр limit_published_date, datetime. Новости будут браться с datetime > limit_published_date
    process.crawl(TNVSpider,
                  limit_published_date=datetime.datetime(2021, 5, 5, 21, 4))
    process.start()
