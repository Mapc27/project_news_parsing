import datetime
import unicodedata

import scrapy
from scrapy.loader import ItemLoader

from news.items import NewsItem
from news.source.config import T2_URL


class Tatarstan24Spider(scrapy.Spider):
    name = 'Tatarstan24'
    start_urls = ['https://tatarstan24.tv/']
    url = T2_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.media-list'):

            date = news.css('div.media-list__date::text').extract_first().strip()
            date = datetime.datetime.strptime(date, "%H:%M %d.%m.%Y")

            if date <= self.limit_published_date:
                self.completed = True
                break
            yield {'date': date.__str__()}
            href = news.css('a.media-list__head').css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        loader = ItemLoader(item=NewsItem(), selector=response)

        published_date = response.css('a.page-main__publish__date::text').extract_first().strip()

        published_date = datetime.datetime.strptime(published_date, "%H:%M %d.%m.%Y")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        text = ' '.join(response.css('div.page-main__text').css('p::text').extract())

        # loader.add_value('from_site', self.name)
        # loader.add_value('published_date', published_date.__str__())
        # loader.add_css('title', 'h1.page-main__head')
        # loader.add_value('href', response.url)
        # loader.add_value('text', text)
        #
        # self.lst.append(loader.load_item())
        #
        # yield loader.load_item()
        title = response.css('h1.page-main__head::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')

        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.page-main__text').css('p ::text')
                        .extract()).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
        text = unicodedata.normalize("NFKD", text)

        out = {
            'from_site': self.name,
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }
        print(out)
        self.lst.append(out)

    def close(self, spider, reason):
        self.output_callback(self.lst)
