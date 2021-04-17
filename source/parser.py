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
from datetime import date, timedelta, datetime


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

    def get_data(self, url: str) -> str:
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
        return r.text

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
            date_ = date.today().strftime('%d %B')
        time_and_date = date_ + ' ' + time
        title = news.find(class_='post__title').text
        subtitle = news.find(class_='post__description').text  # здесь будет дублирование с текстом новости
        print(href, time_and_date, title, subtitle)

        return {'href': href,
                'time': time_and_date,
                'title': title,
                'subtitle': subtitle}

    def get_news_text(self, url):
        current_news_html = self.get_data(url)
        soup = BeautifulSoup(current_news_html, 'lxml')
        full_text = soup.find_all('p')
        useful_text = ''
        for paragraph in full_text:
            if 'Читайте также:' in paragraph.text:
                continue
            useful_text += paragraph.text
        return useful_text


class RealnoeVremyaParser(Parser):
    def __init__(self):
        super().__init__()
        self.url = config.RV_URL

    def create_url(self, day_month_year: str, page: int = 1) -> str:
        return self.url + day_month_year + '?&page=' + str(page)

    # Yet is not used. Can be used to set uniform date
    @staticmethod
    def to_eng_month(rus_mon: str) -> str:
        convert_dict = {'янв': '01',
                        'фев': '02',
                        'мар': '03',
                        'апр': '04',
                        'май': '05',
                        'июн': '06',
                        'июл': '07',
                        'авг': '08',
                        'сен': '09',
                        'окт': '10',
                        'ноя': '11',
                        'дек': '12'}
        try:
            mon = convert_dict[rus_mon]
        except:
            mon = rus_mon
        return mon

    # Yet is not used. Can be used to set uniform date
    def to_iso_date(self, rus_date: str):
        month = self.to_eng_month(rus_date[3:6])
        return

    # yields a today's date in the website format
    @staticmethod
    def set_current_date() -> str:
        return date.today().strftime("%d.%m.%Y")

    # converts from a website date to a datetime instance
    @staticmethod
    def date_from_appropriate(date_on_website: str) -> 'datetime.date':
        date_list = date_on_website.split('.')
        return date(year=int(date_list[2]), month=int(date_list[1]), day=int(date_list[0]))

    # converts from a datetime instance to a website date
    @staticmethod
    def date_to_appropriate(date: 'datetime.date') -> str:
        return date.strftime("%d.%m.%Y")

    # yields a previous date as an instance of class date
    @staticmethod
    def previous_date(date: 'datetime.date') -> 'datetime.date':
        return date - timedelta(days=1)

    # first creates an instance of date class, then sets previous date, then formats back to website date
    def set_new_day(self, website_date: str) -> str:
        datetime_date = self.previous_date(self.date_from_appropriate(website_date))
        return self.date_to_appropriate(datetime_date)

    def border_of_pages(self, url: str) -> int:
        """
        :param url: url of a page for particular date
        :return: a number of pages for particular date
        """
        soup = BeautifulSoup(self.get_data(url), 'lxml')
        try:
            border = int(soup.find(class_='pageNav').find_all('li')[-1].text)
        except:
            border = 1   # execute when there is only one page
        return border

    #  day_month_year has following appearance: dd.mm.yyyy, like on website
    def get_last_news(self, day_month_year: str, page: int = 1):
        current_html = self.get_data(self.create_url(day_month_year, page))
        soup = BeautifulSoup(current_html, 'html.parser')
        all_news = soup.find_all(class_='card withPic leftPic')
        return all_news

    def cut_news(self, news: 'BeautifulSoup') -> dict:
        href = 'https://realnoevremya.ru' + news.find('a').get('href')
        time = news.find(class_='border date').text
        if len(time) == 5:   # Because time in today's news has following format: hh:mm. 5 symbols altogether.
            time = str(date.today()) + ' ' + time
        title = news.find('strong').text

        return {'href': href,
                'time': time,
                'title': title}

    def get_news_text(self, url):
        pass


class Tatarstan24Parser(Parser):
    def __init__(self):
        super().__init__()
        self.url = config.T2_URL

    # TODO: will return date and time in the uniform format
    def unify_time(self, any_time: str) -> str:
        return any_time

    def get_last_news(self, page: int = 1) -> list:
        html = self.get_data(self.url + str(page))
        soup = BeautifulSoup(html, 'html.parser')
        news_container = soup.find(class_='page-grid__content').find(class_='panel-group').find(class_='layout__body')
        return news_container.find(class_='container-underline-list').find_all('li')

    def cut_news(self, news: 'BeautifulSoup') -> dict:
        href = news.find('a').get('href')
        time = news.find(class_='media-list__date').text.strip()
        uni_time = self.unify_time(time)
        title = news.find('a').text.strip()
        subtitle = news.find(class_='media-list__text').text.strip()

        return {'href': href,
                'time': uni_time,
                'title': title,
                'subtitle': subtitle}

    def get_news_text(self, url:str) -> str:
        html = self.get_data(url)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.find(class_='page-main__text').text
        return text


class EveningKazanParser(Parser):
    def __init__(self):
        super().__init__()
        self.url = source.config.EK_URL
        self.page = 0
        self.ls = []
        self._last_published_news_title = 'Мишустин распорядился выплатить деньги туристам, чьи путевки, купленные до конца марта 2020 года, были аннулированы'
        self._last_published_news_time = '16.04.21 09:17'

    def get_data(self, url):
        r = requests.get(f'{url}+{str(self.page)}')
        return r.content

    def change_page(self):
        self.page += 1
        ek.cut_news(ek.get_last_news())

    def get_last_news(self):
        soup = BeautifulSoup(ek.get_data(self.url), 'lxml')
        all_news = soup.find_all('div', class_='views-field-title')

        return all_news

    def get_time(self):
        soup = BeautifulSoup(ek.get_data(self.url), 'lxml')
        all_time = soup.find_all('div', class_='views-field-created')

        return all_time

    def cut_news(self, news):
        times = ek.get_time()
        for j in range(len(news)-3):
            href = self.url[:28] + news[j].find('a').get('href')
            title = news[j].find('a').text
            time = times[j].find('span').text
            if title == self._last_published_news_title and time == self._last_published_news_time:
                self.page =0
                return self.ls
            self.ls.append({'href': href,
                            'title': title,
                            'time': time})
        ek.change_page()
        return self.ls

    # not the end result
    def get_news_text(self, url):
        soup = BeautifulSoup(ek.get_data(self.url), 'lxml')
        all_text = soup.find_all('div', class_='field-content')
        news_text = []
        for text in all_text:
            t = text.text
            news_text.append(t)

        return news_text


if __name__ == '__main__':
    ek = EveningKazanParser()
    cutnews = ek.cut_news(ek.get_last_news())
    for k in range(len(cutnews)):
        print(cutnews[k])

    ti = TatarInformParser()

    response = requests.get(source.config.BG_URL + "2")

    soup = BeautifulSoup(response.text)

    all_news = soup.find_all(class_="article-news")
    print(all_news)
    print(len(all_news))

    # an example of usage for Kazan First:
    kf = KazanFirstParser()
    for p in range(1, 11):
        a_news = kf.get_last_news(p)
        for n in a_news:
            was_cut = kf.cut_news(n)
            print(kf.get_news_text(was_cut['href']))

    # an example of usage for Realnoe Vremya:
    rv = RealnoeVremyaParser()
    date_ = rv.set_current_date()
    for day in range(3):
        current_day_url = rv.create_url(date_, page=1)
        for p in range(1, rv.border_of_pages(current_day_url) + 1):
            print(f'------------ news for {day} day, page {p} ------------')
            last_news = rv.get_last_news(date_, page=p)
            for n in last_news:
                print(rv.cut_news(n))
        date_ = rv.set_new_day(date_)

    # an example of usage Tatarstan24Parser
    t24 = Tatarstan24Parser()
    for p in range(2):
        all_n = t24.get_last_news(p)
        for n in all_n:
            was_cut = t24.cut_news(n)
            print(was_cut)
            print("------------TEXT NEWS------------")
            print(t24.get_news_text(was_cut['href']))