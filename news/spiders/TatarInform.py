import datetime
import unicodedata

import scrapy
from scrapy.loader import ItemLoader

from news.items import NewsItem
from news.source.config import months_names, TI_URL


class TatarInformSpider(scrapy.Spider):
    name = 'TatarInform'
    start_urls = ['https://www.tatar-inform.ru/news/widget/list/novosti/page/']
    url = TI_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_published_date = kwargs.get('limit_published_date', None)
        self.output_callback = kwargs.get('callback', None)
        self.completed = False
        self.lst = []

    def start_requests(self):
        yield scrapy.Request(self.url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('li.underline-list__item'):

            date = news.css('div.list-item__date::text').extract()
            for i in range(len(date)):
                date[i] = date[i].strip()
            date = ' '.join(date)

            for i in range(1, len(months_names)):
                if months_names[i] in date:
                    date = date.replace(months_names[i], str(i))
                    break

            date = datetime.datetime.strptime(date, "%H:%M %d %m %Y")

            if date <= self.limit_published_date:
                self.completed = True
                break

            href = news.css('div.list-item__content').css('a::attr(href)').extract_first()

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("/")[-1])
            yield response.follow(self.url + str(current_page+1), callback=self.parse)

    def parse_news(self, response):
        loader = ItemLoader(item=NewsItem(), selector=response)

        published_date = response.css('div.page-main__publish-data').css('a::text').extract_first().strip()
        published_date = published_date.replace(u'\xa0\xa0', u' ')

        month = published_date.split(' ')[1]
        replace = months_names.index(month.lower())

        published_date = published_date.replace(month, str(replace))
        published_date = datetime.datetime.strptime(published_date, "%d %m %Y %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        # loader.add_value('from_site', self.name)
        # loader.add_value('published_date', published_date.__str__())
        # loader.add_css('title', 'h1.page-main__title')
        # loader.add_value('href', response.url)
        # loader.add_css('text', 'div.page-main__text')
        #
        # self.lst.append(loader.load_item())
        #
        # yield loader.load_item()
        title = response.css('h1.page-main__title::text').extract_first().strip() \
            .replace(u'\r', u'').replace(u'\n', u'')

        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.page-main__text').css('p ::text').extract()).strip() \
            .replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
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

