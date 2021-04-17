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
import source.config
import json


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
        self.url = source.config.TI_URL

    def get_last_news(self, page: int = 1):
        """
        gets last 15 news in one page
        if you need to get more news, you should pass argument page

        page = 1 is last news
        :param page: number of page
        :return: list of dictionaries
                 dictionary - information about news
        """

        response = self.get_data(source.config.TI_URL + str(page))

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
        self.url = source.config.BG_URL

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


class EveningKazanParser:
    def __init__(self):
        super().__init__()
        self.url = source.config.EK_URL
        self._last_published_news_title = 'В Нижнекамске нашли школьника, который вышел из дома и пропал'
        self._last_published_news_time = '17.04.21 10:17'

    def get_data(self, url, i=0):
        r = requests.get(f'{url}+{i}')
        return r.content

    def get_last_news(self, page: int = 1):
        soup = BeautifulSoup(ek.get_data(self.url), 'lxml')
        all_news = soup.find_all('div', class_='views-field-title')

        return all_news

    def get_time(self):
        soup = BeautifulSoup(ek.get_data(self.url), 'lxml')
        all_time = soup.find_all('div', class_='views-field-created')

        return all_time

    def cut_news(self, news, times):
        ls = []
        for j in range(len(news)-3):
            href = self.url[:28] + news[j].find('a').get('href')
            title = news[j].find('a').text
            date_time = times[j].find('span').text
            if title != self._last_published_news_title or date_time != self._last_published_news_time:
                date_time = date_time.split(' ')
                date = date_time[0]
                time = date_time[1]
                ls.append({'href': href,
                           'title': title,
                           'date': date,
                           'time': time})
            else:
                return ls
        return ls


if __name__ == '__main__':
    ek = EveningKazanParser()
    # print(ek.get_data(source.config.EK_URL))
    # print(ek.get_last_news())
    for k in range(len(ek.cut_news(ek.get_last_news(), ek.get_time()))):
        print(ek.cut_news(ek.get_last_news(), ek.get_time())[k])

    # ti = TatarInformParser()
    #
    # response = requests.get(source.config.BG_URL + "2")
    #
    # soup = BeautifulSoup(response.text)
    #
    # all_news = soup.find_all(class_="article-news")
    # print(all_news)
    # print(len(all_news))
