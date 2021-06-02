import datetime
import unicodedata

import scrapy
from scrapy.loader import ItemLoader

from news.items import NewsItem
from news.source.config import RV_URL


class RealnoeVremyaSpider(scrapy.Spider):
    name = 'RealnoeVremya'
    start_urls = ['https://realnoevremya.ru']
    url = RV_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.completed = False
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('li.withPic'):
            date = news.css('span.date::text').extract_first().strip()
            time = date.split(' ')[-1]
            date = response.url.split('/')[-1]
            if len(date.split('.')) == 1:
                date = datetime.datetime.now()
                day = date.day
                month = date.month
                year = date.year
                date = time + ', ' + str(day) + '.' + str(month) + '.' + str(year)
            else:
                date = time + ', ' + date
            date = datetime.datetime.strptime(date, "%H:%M, %d.%m.%Y")

            if date <= self.limit_published_date:
                self.completed = True
                break

            href = news.css('a::attr(href)').extract_first()

            yield response.follow(self.start_urls[0] + href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            next_page = response.css('div.headerBlock').css('span.nowrap').css('a::attr(href)').extract_first()

            yield response.follow(self.start_urls[0] + next_page, callback=self.parse)

    def parse_news(self, response):
        loader = ItemLoader(item=NewsItem(), selector=response)

        published_date = response.css('div.dateLine').css('a::text').extract_first().strip()
        published_date = datetime.datetime.strptime(published_date, "%H:%M, %d.%m.%Y")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        text = ' '.join(response.css('div.detailCont').css('p ::text').extract())

        # loader.add_value('from_site', self.name)
        # loader.add_value('published_date', published_date.__str__())
        # loader.add_css('title', 'div.detailCont > article > h1')
        # loader.add_value('href', response.url)
        # loader.add_value('text', text)
        #
        # self.lst.append(loader.load_item())
        #
        # yield loader.load_item()
        title = response.css('div.detailCont').css('h1::text').extract_first().strip() \
            .replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.detailCont').css('p ::text').extract()) \
            .replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
        text = unicodedata.normalize("NFKD", text)
        out = {
            'from_site': self.name,
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }
        self.lst.append(out)
        print(out)

    def close(self, spider, reason):
        self.output_callback(self.lst)
