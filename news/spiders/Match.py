import scrapy

from news.source.config import headers, percentage_of_similarity
import re


class MatchSpider(scrapy.Spider):

    # """
    # :news_list Принимает [[other_news, ti_news_1], [other_news, ti_news_2], [other_news, ti_news_3], ...]
    # :return {other_news, 'is_match': True/False}
    # """

    name = 'Match'
    start_urls = ['https://utext.rikuz.com/index.php']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.news_pair_lst = kwargs.get('news_lst', None)
        self.output_callback = kwargs.get('callback', None)
        self.max_match = 0
        self.ti_news_match_id = None

    def start_requests(self):
        for news_tuple in self.news_pair_lst:
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
                cb_kwargs={'ti_news': news_tuple[1]},
            )

    def parse(self, response, **kwargs):
        regex = re.compile('(\d{1,3}[.]\d{1,2}[%])|(\d{1,3}[%])')

        match = regex.search(response.text).group(0)
        match = float(match[:-1])

        if match > self.max_match:
            self.max_match = match
            self.ti_news_match_id = kwargs.get('ti_news', None)['id']

    def close(self, spider, reason):
        news = self.news_pair_lst[0][0]
        if self.max_match > percentage_of_similarity:
            news['is_match'] = True
            news['ti_id'] = self.ti_news_match_id
        else:
            news['is_match'] = False
        self.output_callback(news)
