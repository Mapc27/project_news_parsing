# ATTENTION ЭТО МОЁ ВИДЕНИЕ ПРОЕКТА. ПИШУ ЭТО ЗДЕСЬ, ЧТОБЫ НЕ ЗАБЫТЬ МЫСЛИ.
# ЕСЛИ У ВАС ЕСТЬ ПРЕДЛОЖЕНИЯ, ТО НУЖНО СООБЩАТЬ О НИХ

# Парсеры под каждый сайт

from abc import abstractmethod
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
import lxml


class Parser:
    """
    Собирает информация с сайта новостей
    """
    @abstractmethod
    def __init__(self):
        self._url: str
        self._html: str

        self._last_published_news_title: str
        self._last_published_news_time: datetime

    def get_data(self):
        driver = webdriver.Chrome()
        driver.get(url=self._url)

        self.html = driver.page_source

        # with requests.session() as s:
        #     response = s.get(self.url)
        #     print(response.text)
        #
        # text = response.text
        # text.decode(encoding).encode("utf-8")
        #
        # self.html = text
        # return response.text

    @abstractmethod
    def get_last_news(self):
        pass

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, html):
        self._html = html

    @property
    def last_published_news_title(self):
        return self._last_published_news_title

    @last_published_news_title.setter
    def last_published_news_title(self, last_published_news_title):
        self._last_published_news_title = last_published_news_title

    @property
    def last_published_news_time(self):
        return self._last_published_news_time

    @last_published_news_time.setter
    def last_published_news_title(self, last_published_news_time):
        self._last_published_news_time = last_published_news_time


class TatarInformParser(Parser):
    def __init__(self):
        super().__init__()
        self._url = 'https://www.tatar-inform.ru/'

    def get_last_news(self):
        soup = BeautifulSoup(self._html, 'lxml')

        all_news = soup.find(class_="ct-fc-items")
        print(len(all_news))
        print(all_news.text)
        return all_news


# def whatisthis(s):
#     if isinstance(s, str):
#         print("ordinary string")
#     if isinstance(s, unicode):
#         print("unicode string")
#     else:
#         print("not a string")


if __name__ == '__main__':
    fiele = TatarInformParser()
    file = fiele.get_data()
    # fiele.get_last_news()
    # print(fiele.html)
    # fiele.html = 'fdfd'
    # print(fiele.html)

    # whatisthis(file)