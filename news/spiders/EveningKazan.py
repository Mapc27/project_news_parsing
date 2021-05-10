import datetime
import unicodedata
import scrapy


from .config import EK_URL


class EveningKazanSpider(scrapy.Spider):
    name = 'EveningKazan'
    start_urls = ['https://www.evening-kazan.ru']
    url = EK_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        yield scrapy.Request(self.url + '0', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.view-content').css('div.views-field-title'):

            href = news.css('a::attr(href)').extract_first()
            href = self.start_urls[0] + href

            yield response.follow(href, callback=self.parse_news)

            if self.completed:
                break

        if not self.completed:
            current_page = int(response.url.split("=")[-1])
            yield response.follow(self.url + str(current_page + 1), callback=self.parse)

    def parse_news(self, response):
        published_date = response.css('div.heading--meta-wrap').css('div.submitted::text').extract_first().strip()

        published_date = datetime.datetime.strptime(published_date, "%d.%m.%y %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('div.sidebar-both').css('h1.title::text')\
            .extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.sidebar-both').css('div.content ::text')
                        .extract()).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
        text = unicodedata.normalize("NFKD", text)

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }
