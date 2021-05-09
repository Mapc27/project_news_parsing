import datetime
import unicodedata

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import KF_URL, months_names


class KazanFirstSpider(scrapy.Spider):
    name = 'KazanFirst'
    start_urls = ['https://kazanfirst.ru/']
    url = KF_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        yield scrapy.Request(self.url.format(1), callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('a'):

            href = news.css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            # 'https://kazanfirst.ru/news?content_only=1&page={}&limit=15&start_limit=15'
            left = response.url.rfind('page=')
            right = response.url.find('&limit')
            current_page = int(response.url[left+5:right])

            yield response.follow(self.url.format(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('div.post-info')

        time = published_date.css('span.post-info__time::text').extract_first().strip()
        date = published_date.css('span.post-info__date::text').extract_first().strip()

        published_date = time + ' ' + date

        # если год указан(не текущий год, например, 2020 или 2019)
        if published_date.split(' ')[-1].isdigit():
            month = published_date.split(' ')[-2]
            replace = months_names.index(month.lower())

            published_date = published_date.replace(month, str(replace))
            published_date = datetime.datetime.strptime(published_date, "%H:%M %d %m %Y")
        # год не указан, указываем текущий
        else:
            month = published_date.split(' ')[-1]
            replace = months_names.index(month.lower())

            published_date = published_date.replace(month, str(replace))
            published_date += ' ' + str(datetime.datetime.now().year)
            published_date = datetime.datetime.strptime(published_date, "%H:%M %d %m %Y")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('h1.content__title::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.infinite-container').css('p ::text')
                        .extract()[:-2]).strip().replace(u'\r', u'').replace(u'\n', u'')
        text = unicodedata.normalize("NFKD", text)

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl(KazanFirstSpider,
                  limit_published_date=datetime.datetime(2021, 5, 8, 21, 4))
    process.start()
