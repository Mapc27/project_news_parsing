# -*- coding: utf-8 -*-
# ATTENTION ЭТО МОЁ ВИДЕНИЕ ПРОЕКТА. ПИШУ ЭТО ЗДЕСЬ, ЧТОБЫ НЕ ЗАБЫТЬ МЫСЛИ.
# ЕСЛИ У ВАС ЕСТЬ ПРЕДЛОЖЕНИЯ, ТО НУЖНО СООБЩАТЬ О НИХ

# Парсеры под каждый сайт

from abc import abstractmethod
from datetime import datetime

import requests
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
        options = webdriver.ChromeOptions()
        options.headless = True

        driver = webdriver.Chrome(options=options)
        driver.get(url=self._url)

        self.html = driver.page_source

        # with requests.session() as s:
        #
        #     response = s.get(self.url)
        #     text = response.text
        #
        # text = text.encode('utf-8')
        # print(text)
        # self.html = text
        #
        # r = requests.get(self.url)
        # print(r.encoding)
        # self.html = r.text

    @abstractmethod
    def get_last_news(self):
        pass

    @abstractmethod
    def cut_news(self):
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
    def last_published_news_time(self, last_published_news_time):
        self._last_published_news_time = last_published_news_time


class TatarInformParser(Parser):
    def __init__(self):
        super().__init__()
        self.url = 'https://www.tatar-inform.ru/'

        self.get_data()

    def get_last_news(self):
        soup = BeautifulSoup(self.html, 'lxml')
        all_news = soup.find_all(class_="ct-fc-item")

        return all_news

    def cut_news(self):
        news_html = self.get_last_news()

        for new in news_html:
            href = new.get('href')
            time = new.find(class_="ct-fc-item-time").text
            title = new.find(class_="ct-fc-item-title-text").text
            print(href, time, title)
            break


if __name__ == '__main__':
    ti = TatarInformParser()
    ti.cut_news()
