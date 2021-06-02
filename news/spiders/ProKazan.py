import datetime
import unicodedata

import scrapy
from scrapy.loader import ItemLoader

from news.items import NewsItem
from news.source.config import RU_PK_URL, KZN_PK_URL


class ProKazanSpider(scrapy.Spider):
    name = 'ProKazan'
    start_urls = ['https://prokazan.ru']
    ru_url = RU_PK_URL
    kzn_url = KZN_PK_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.ru_url + '1', callback=self.parse)
        yield scrapy.Request(self.kzn_url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.news-mid__content'):

            day = news.css('div.news-mid__date').css('p.news-mid__day::text').extract_first().strip()
            time = news.css('div.news-mid__date').css('p.news-mid__time::text').extract_first().strip()

            if day == 'сегодня' or len(day.split('.')) == 1:
                today = datetime.datetime.now()
                date = str(today.day) + '.' + str(today.month) + '.' + str(today.year) + ', ' + time
            else:
                date = day + ', ' + time

            date = datetime.datetime.strptime(date, "%d.%m.%Y, %H:%M")

            if date <= self.limit_published_date:
                self.completed = True
                break

            href = news.css('a::attr(href)').extract_first()
            href = self.start_urls[0] + href

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            n = response.url.rfind('/')
            current_page = int(response.url[n+1:])
            url = response.url[:n+1]
            yield response.follow(url + str(current_page + 1), callback=self.parse)

        self.completed = False

    def parse_news(self, response):
        loader = ItemLoader(item=NewsItem(), selector=response)

        published_date = response.css('span.article-info__date::text').extract_first().strip()
        published_date = datetime.datetime.strptime(published_date, "%d.%m.%Y, %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        # loader.add_value('from_site', self.name)
        # loader.add_value('published_date', published_date.__str__())
        # loader.add_css('title', 'h1.article__name')
        # loader.add_value('href', response.url)
        # loader.add_css('text', 'div.ArticleContent')
        #
        # self.lst.append(loader.load_item())
        #
        # yield loader.load_item()
        title = response.css('h1.article__name::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.ArticleContent ::text')
                        .extract()).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
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
