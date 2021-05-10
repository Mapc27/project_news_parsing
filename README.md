# Ссылки

### Trello:
https://trello.com/b/OiRwZ3Gi/news-parsing

### Google Drive:
https://drive.google.com/drive/folders/1b15yjrtGpKQdG5_Awp6abk3pZxktcOc_?usp=sharing


# Используемые технологии

### Python 3.7.x
    scrapy (pip install scrapy)
    SQLite
    SQLAlchemy

### Database SQLAlchemy

# Структура проекта:
need to update
- [`source`](source) - папка с кодом проекта.
  - [`parser.py`](source/parser.py) - файл сбора новостей
  - [`db.py`](source/db.py) - файл работа с базой данных
  - [`match.py`](source/match.py) - файл сравнение новостей
  - [`parser.py`](source/parser.py) - файл с кодом сбора новостей
  - [`main.py`](main.py) - файл основная логика проекта
- [`news`](news) - папка scrapy для парсинга
  - [`spiders`](news/spiders) - папка с пауками scrapy
    - [`config.py`](news/spiders/config.py) - файл конфигураций для пауков
  