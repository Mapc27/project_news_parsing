# Ссылки

### Trello:
https://trello.com/b/OiRwZ3Gi/news-parsing

### Google Drive:
https://drive.google.com/drive/folders/1b15yjrtGpKQdG5_Awp6abk3pZxktcOc_?usp=sharing


# Используемые технологии

### Python 3.7.x
    requests (pip install requests)
    BS4 (pip install beautifulsoup4)
    lxml (pip install lxml) <soup = BeautifulSoup(html, 'lxml')>
    PostgreSQL
    Selenium (pip install Selenium)

### Database SQLAlchemy

# Структура проекта:
need to update
- [`source`](source) - папка с кодом проекта.
  - [`parser.py`](source/parser.py) - файл сбора новостей
  - [`db.py`](source/db.py) - файл работа с базой данных
  - [`match.py`](source/match.py) - файл сравнение новостей
  - [`parser.py`](source/parser.py) - файл с кодом сбора новостей
  - [`main.py`](source/main.py) - файл основная логика проекта
  - [`config.py`](source/config.py) - файл конфигураций
- [`ChromeDriver`](ChromeDriver) - папка, в которой лежит драйвер Хром.
    - [`chromedriver.exe`](ChromeDriver/chromedriver.exe) - драйвер Хром.
    