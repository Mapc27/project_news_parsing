import datetime
import unicodedata
import scrapy


from .config import TNV_URL, months_names


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

    def parse_news(self, response, requests_count=0):
        try:
            published_date = response.css('div.novelty__information').css('p.novelty__date::text')\
                .extract_first().strip()

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

            text = ' '.join(array).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
            text = unicodedata.normalize("NFKD", text)

            yield {
                'published_date': published_date.__str__(),
                'title': title,
                'href': href,
                'text': text,
            }
        except AttributeError:
            if requests_count > 5:
                return
            yield response.follow(response.url, callback=self.parse_news, dont_filter=True, method='POST',
                                  cb_kwargs={'requests_count': requests_count+1})
