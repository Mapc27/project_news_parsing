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
    def __init__(self):
        self.url: str = ''
        self.html: str = ''

        self.last_published_news_title: str = ''
        self.last_published_news_time: datetime

    def get_data(self):
        driver = webdriver.Chrome()
        driver.get(url=self.url)

        self.html = driver.page_source

    @abstractmethod
    def get_last_news(self):
        """

        :return:
        """
        pass


class TatarInformParser(Parser):
    def get_last_news(self):
        soup = BeautifulSoup(self.html, 'lxml')

        all_news = soup.find(class_="ct-fc-items")
        print(len(all_news))
        return all_news


if __name__ == '__main__':
    parser = TatarInformParser()
    parser.get_data()

    print(parser.get_last_news())
