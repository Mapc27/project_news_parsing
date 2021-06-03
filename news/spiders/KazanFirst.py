import datetime

import scrapy
from scrapy.loader import ItemLoader

from news.items import CompetitorsNewsItem
from news.source.config import KF_URL, months_names


class KazanFirstSpider(scrapy.Spider):
    name = 'KazanFirst'
    start_urls = ['https://kazanfirst.ru/']
    url = KF_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url.format('1'), callback=self.parse, dont_filter=True)

    def parse(self, response, **kwargs):
        for news in response.css('a'):

            href = news.css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            left = response.url.rfind('page=')
            right = response.url.find('&limit')
            current_page = int(response.url[left+5:right])

            yield response.follow(self.url.format(str(current_page + 1)), callback=self.parse)

    def parse_news(self, response):
        loader = ItemLoader(item=CompetitorsNewsItem(), selector=response)

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

        text = ' '.join(response.css('div.infinite-container').css('p ::text')
                        .extract()[:])

        loader.add_value('from_site', self.name)
        loader.add_value('published_date', published_date)
        loader.add_css('title', 'h1.content__title')
        loader.add_value('href', response.url)
        loader.add_value('text', text)

        self.lst.append(loader.load_item())

        print(loader.load_item())

    def close(self, spider, reason):
        self.output_callback(self.lst)
