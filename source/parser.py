# -*- coding: utf-8 -*-
# ATTENTION ЭТО МОЁ ВИДЕНИЕ ПРОЕКТА. ПИШУ ЭТО ЗДЕСЬ, ЧТОБЫ НЕ ЗАБЫТЬ МЫСЛИ.
# ЕСЛИ У ВАС ЕСТЬ ПРЕДЛОЖЕНИЯ, ТО НУЖНО СООБЩАТЬ О НИХ

# Парсеры под каждый сайт

from abc import abstractmethod, ABC
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import lxml
import config
import json
from datetime import date


class Parser:
    """
    Собирает информацию с сайта новостей
    """
    @abstractmethod
    def __init__(self):
        self._url: str
        self._html: str

        self._last_published_news_title: str
        self._last_published_news_time: datetime

    def get_data(self, url):
        # with selenium webdriver
        # a very long time
        # options = webdriver.ChromeOptions()
        # options.headless = True
        #
        # driver = webdriver.Chrome(options=options)
        # driver.get(url=url)
        #
        # return driver.page_source

        # with requests
        # very fast method

        r = requests.get(url)
        return r.content

    @abstractmethod
    def get_last_news(self):
        pass

    @abstractmethod
    def cut_news(self, new):
        pass

    @abstractmethod
    def get_news_text(self, url):
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


class TatarInformParser(Parser, ABC):
    def __init__(self):
        super().__init__()
        self.url = config.TI_URL

    def get_last_news(self, page: int = 1):
        """
        gets last 15 news in one page
        if you need to get more news, you should pass argument page

        page = 1 is last news
        :param page: number of page
        :return: list of dictionaries
                 dictionary - information about news
        """

        response = self.get_data(config.TI_URL + str(page))

        # from str does python object
        list_of_dicts_news = json.loads(response.content)
        # type(list_of_dictionaries) = list

        return list_of_dicts_news

    def cut_news(self, news):
        """
        needs for break down news (one)
        :param news: one news dict
        :return:  (for now) tuple(id, published_date, title, text, lead, url)
        """
        # todo
        pass


class BusinessGazetaParser(Parser):
    def __init__(self):
        super().__init__()
        self.url = config.BG_URL

    def get_last_news(self, page: int = 1):
        """
        gets last 20 news in one page
        if you need to get more news, you should pass argument page

        page = 1 is last news
        :param page: number of page
        :return: list of dictionaries
                 dictionary - information about news
        """

        # теперь будет реализация через requests
        # url изменился он есть в config нужно посмотреть и спарсить новости.
        # думаю ниже код уже не будет работать
        # нужно возвращать что-то по аналогии с татар-информ
        # к url добавляем номер страницы (response = self.get_data(config.TI_URL + str(page)))

        soup = BeautifulSoup(self.html, 'lxml')
        all_news = soup.find_all(class_="last-news__item region1 type99")

        return all_news

    def cut_news(self, news):
        href = self.url[:-1:] + news.find(class_='last-news__link').get('href')
        time = news.find(class_="last-news__time").text
        title = news.find(class_="last-news__link").text
        print(href, time, title)
        return {'href': href,
                'time': time,
                'title': title}

    def get_news_text(self, url):
        soup = BeautifulSoup(self.get_data(url), 'lxml')
        news_text = soup.find('div', class_="articleBody").text
        return news_text


class KazanFirstParser(Parser, ABC):
    def __init__(self):
        super().__init__()
        self.url = config.KF_URL

    def get_last_news(self, page: int = 1):
        current_html = self.get_data(self.url + str(page))
        soup = BeautifulSoup(current_html, 'lxml')
        all_news = soup.find_all(class_='post-item column-list__item js-column-item')
        return all_news

    def cut_news(self, news: 'BeautifulSoup') -> dict:
        href = news.get('href')
        time = news.find(class_='post-info__time').text
        try:
            date_ = news.find(class_='post-info__date').text
        except:
            date_ = date.today().strftime('%d %b')
        time_and_date = date_ + ' ' + time
        title = news.find(class_='post__title').text
        subtitle = news.find(class_='post__description').text
        print(href, time_and_date, title, subtitle)

        return {'href': href,
                'time': time_and_date,
                'title': title,
                'subtitle': subtitle}

    def get_news_text(self, url):
        pass


if __name__ == '__main__':
    ti = TatarInformParser()

    response = requests.get(config.BG_URL + "2")

    soup = BeautifulSoup(response.text)

    all_news = soup.find_all(class_="article-news")
    print(all_news)
    print(len(all_news))

    # example of usage:
    kf = KazanFirstParser()
    for p in range(1, 11):
        a_news = kf.get_last_news(p)
        for n in a_news:
            kf.cut_news(n)

