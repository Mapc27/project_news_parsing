import scrapy
from scrapy.crawler import CrawlerProcess

from news.source.config import headers
import re


class MatchSpider(scrapy.Spider):
    name = 'Match'
    start_urls = ['https://utext.rikuz.com/index.php']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.news_lst = kwargs.get('news_lst', 'None')
        self.output_callback = kwargs.get('callback', None)
        self.lst = []

    def start_requests(self):
        for news_tuple in self.news_lst:
            params = {'text1': news_tuple[0]['text'],
                      'text2': news_tuple[1]['text'],
                      'lang': 'ru',
                    }

            yield scrapy.FormRequest(
                url=self.start_urls[0],
                method='POST',
                headers=headers,
                formdata=params,
                callback=self.parse,
                cb_kwargs={'news': news_tuple[1]}
            )

    def parse(self, response, **kwargs):
        regex = re.compile('\d{1,3}[.]\d{1,2}[%]')
        match = regex.findall(response.text)[0]
        match = float(match[:-1])
        self.lst.append(match)

    def close(self, spider, reason):
        max_match = max(self.lst)
        news = self.news_lst[0][0]
        if max_match > 15.0:
            news['match'] = 'True'
        else:
            news['match'] = 'False'
        self.output_callback(news)
