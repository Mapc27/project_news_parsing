import datetime

import scrapy
from scrapy.loader import ItemLoader

from news.items import CompetitorsNewsItem
from news.source.config import BG_URL, months_names


class BusinessGazetaSpider(scrapy.Spider):
    name = 'BusinessGazeta'
    start_urls = ['https://www.business-gazeta.ru/news']
    url = BG_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.completed = False
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('article.article-news')[1:]:
            date = news.css('span.article-news__datetime').css('a::text').extract_first()

            if date is not None:
                date = date.strip().split(' ')

                day = int(date[0])
                month = months_names.index(date[1].lower())

                # если дата только такая: 28 Мая
                if len(date) == 2:
                    year = datetime.datetime.now().year
                # иначе: 14 сентября 2020
                else:
                    year = int(date[2])

                date = datetime.datetime(year=year, month=month, day=day+1, hour=0, minute=0)

                if date <= self.limit_published_date:
                    self.completed = True
                    break

            href = news.css('div.article-news__desc').css('a::attr(href)').extract_first()
            n = href.rfind('/')
            href = href[n:]

            yield response.follow(self.start_urls[0] + href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        loader = ItemLoader(item=CompetitorsNewsItem(), selector=response)

        published_date = response.css('time.article__date::attr(datetime)').extract_first()
        published_date = datetime.datetime.strptime(published_date, "%Y-%m-%dMSK%H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        loader.add_value('from_site', self.name)
        loader.add_value('published_date', published_date)
        loader.add_css('title', 'h1.article__h1')
        loader.add_value('href', response.url)
        loader.add_css('text', 'div.articleBody')

        self.lst.append(loader.load_item())

        print(loader.load_item())

    def close(self, spider, reason):
        self.output_callback(self.lst)
