import datetime
import unicodedata
import scrapy


from .config import RU_PK_URL, KZN_PK_URL


class ProKazanSpider(scrapy.Spider):
    name = 'ProKazan'
    start_urls = ['https://prokazan.ru']
    ru_url = RU_PK_URL
    kzn_url = KZN_PK_URL

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completed = False
        self.limit_published_date = kwargs.get('limit_published_date', None)

    def start_requests(self):
        yield scrapy.Request(self.ru_url + '1', callback=self.parse)
        yield scrapy.Request(self.kzn_url + '1', callback=self.parse)

    def parse(self, response, **kwargs):
        for news in response.css('div.news-mid__content'):

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
        published_date = response.css('span.article-info__date::text').extract_first().strip()

        published_date = datetime.datetime.strptime(published_date, "%d.%m.%Y, %H:%M")

        if published_date <= self.limit_published_date:
            self.completed = True
            return

        title = response.css('h1.article__name::text').extract_first().strip().replace(u'\r', u'').replace(u'\n', u'')
        title = unicodedata.normalize("NFKD", title)

        href = response.url

        text = ' '.join(response.css('div.ArticleContent ::text')
                        .extract()).strip().replace(u'\r', u'').replace(u'\n', u'').replace(u'\t', u'')
        text = unicodedata.normalize("NFKD", text)

        yield {
            'published_date': published_date.__str__(),
            'title': title,
            'href': href,
            'text': text,
        }
