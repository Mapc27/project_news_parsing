import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from news.spiders.Match import MatchSpider
from config import headers

ti_array = []
other_array = []


url = 'https://utext.rikuz.com/index.php'
params = {'text1': 'Об очередном инциденте с участием электротранспорта сообщили очевидцы в соцсетях. На этот раз у трамвая на полном ходу отказали тормоза. Всё произошло на проспекте Победы. Перепуганные пассажиры начали выпрыгивать из салона. В какой-то момент трамвай остановился сам недалеко от остановки "Улица Академика Глушко". По предварительным данным никто из людей не пострадал. К сожалению, происшествия с трамваями в столице Татарстана происходят регулярно. Так, недавно трамвай пятого маршрута сошел с рельсов, чуть ранее трамвай влетел в столб, был случай когда у электротранспорта отвалилась на ходу дверь,  и даже "рогатый" сбил ребенка. ',
        'text2': 'Как рассказали ИА «Татар-информ» свидетели, сегодня в четвертом часу дня на проспекте Победы у трамвая отказали тормоза. «Люди начали выпрыгивать из салона. По-моему, никто не пострадал. Трамвай сам остановился в районе остановки Глушко», – рассказал один из очевидцев событий.',
        'lang': 'ru',
          }


def get_data(url, params):
    response = requests.post(url, data=params, headers=headers)
    return response.text


def scraping(response):
    soup = BeautifulSoup(response, 'lxml')
    print(soup.find('p', class_='check_result').text.strip())


if __name__ == '__main__':
    # scraping(get_data(url, params))
    for i in range(50):
        params['text1'] = str(i) + '1253674548 234 4556 5768 4657687 56788'
        params['text2'] = str(i) + '2342834 45  67 89   23 6576 7 687345 66767 24 20 24 24'
        print(get_data(url, params))
