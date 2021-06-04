# Такие методы, как достать из БД n-ное количество новостей с учётом времени

from contextlib import contextmanager

from sqlalchemy import (Column,
                        Integer,
                        String,
                        DateTime,
                        Boolean,
                        ForeignKey,
                        create_engine,
                        and_,
                        exc,)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

DATABASE_NAME = 'parsed_news.sqlite'

engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind=engine)

Base = declarative_base()


class Website(Base):
    __tablename__ = "website"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name_website = Column(String, default=None)

    def __repr__(self):
        return f"{self.id} | {self.name_website}"


class TINews(Base):
    __tablename__ = "ti_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    published_date = Column(DateTime, default=None)
    title = Column(String, default=None)
    href = Column(String, default=None)
    text = Column(String, default=None)
    match = relationship("CompetitorsNews", backref=backref("matching_news"))

    def __repr__(self):
        return f"{self.id} | {self.published_date} | {self.title}"


class CompetitorsNews(Base):
    __tablename__ = "competitors_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    published_date = Column(DateTime, default=None)
    title = Column(String, default=None)
    href = Column(String, default=None)
    is_match = Column(Boolean, default=False)
    matching_news_id = Column(Integer, ForeignKey("ti_news.id"), default=None)
    website_id = Column(Integer, ForeignKey("website.id"), default=None)

    def __repr__(self):
        if self.is_match:
            return f"{self.id} | link: {self.href} |is match: {self.is_match} | matching news: {self.matching_news.title}"
        return f"{self.id} | link: {self.href} | is match: {self.is_match}"


def create_db():
    Base.metadata.create_all(engine)


@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_session_without_expire():
    session = Session(expire_on_commit=False)
    try:
        yield session
        session.commit()
    except exc.SQLAlchemyError:
        session.rollback()
        raise
    finally:
        session.close()


def get_ti_news(session, published_date_: datetime, title_: str):
    news = session.query(TINews).filter(and_(TINews.published_date == published_date_, TINews.title == title_)).first()
    return news


def ti_news_exists(session, published_date_: datetime, title_: str) -> bool:
    return get_ti_news(session, published_date_, title_) is not None


def add_ti_news(published_date_: datetime, title_: str, href_: str, text_: str):
    with get_session_without_expire() as session:
        if not ti_news_exists(session, published_date_, title_):
            ti_news = TINews(published_date=published_date_, title=title_, href=href_, text=text_)
            session.add(ti_news)


def add_ti_news_list(news: list):
    for entry in news:
        if isinstance(entry['published_date'], str):
            entry['published_date'] = datetime.fromisoformat(entry['published_date'])

        add_ti_news(published_date_=entry['published_date'],
                    title_=entry['title'],
                    href_=entry['href'],
                    text_=entry['text'])


def add_website(session, website):
    website = Website(name_website=website)
    session.add(website)
    return website


def get_website_id(session, name_website_: str):
    website = session.query(Website).filter_by(name_website=name_website_).first()
    return website.id


def get_competitor_news(session, href):
    news = session.query(CompetitorsNews).filter(CompetitorsNews.href == href).first()
    return news


def competitor_news_exists(session, href: str):
    return get_competitor_news(session, href) is not None


def add_competitor_news(published_date_: datetime, title_: str, href_: str, website: str,
                        is_match_: bool, matching_news_id_: int = None):
    with get_session() as session:
        if not competitor_news_exists(session, href_):
            website_id_ = get_website_id(session, website)
            comp_news = CompetitorsNews(published_date=published_date_,
                                        title=title_,
                                        href=href_,
                                        is_match=is_match_,
                                        matching_news_id=matching_news_id_,
                                        website_id=website_id_)
            if is_match_:
                matching_news_ = session.query(TINews).get(matching_news_id_)
                comp_news.matching_news = matching_news_
            session.add(comp_news)


def add_comp_news_list(news: list):
    for entry in news:
        if 'ti_id' not in entry.keys():
            entry['ti_id'] = None

        if isinstance(entry['published_date'], str):
            entry['published_date'] = datetime.fromisoformat(entry['published_date'])

        add_competitor_news(published_date_=entry['published_date'],
                            title_=entry['title'],
                            href_=entry['href'],
                            website=entry['from_site'],
                            is_match_=entry['is_match'],
                            matching_news_id_=entry['ti_id'])


# return ti_news id by matching
def get_matching_news_id(published_date_: datetime, title_: str):
    with get_session_without_expire() as session:
        news = get_ti_news(session, published_date_, title_)
        return news.id


def get_all_ti_news(up_to_time: datetime = None):
    list_ti_news = []
    with get_session() as session:
        if up_to_time:
            ti_news = session.query(TINews).filter(TINews.published_date > up_to_time).all()
        else:
            ti_news = session.query(TINews).all()
        for news in ti_news:
            dic = {'id': news.id,
                   'published_date': news.published_date,
                   'title': news.title,
                   'href': news.href,
                   'text': news.text}
            list_ti_news.append(dic)

    return list_ti_news


def fill_websites():
    with get_session_without_expire() as session:
        comps = ['BusinessGazeta',
                 'EveningKazan',
                 'InKazan',
                 'ProKazan',
                 'RealnoeVremya',
                 'Tatarstan24',
                 'TNV',
                 'KazanFirst']
        for comp in comps:
            add_website(session, comp)


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()

        fill_websites()

    time1 = datetime.fromisoformat("2020-10-20")

    ti_dict1 = {'published_date': '2021-06-02 15:33:00',
                'title': 'title1',
                'href': 'link1',
                'id': 3,
                'text': 'news text 1'}

    ti_dict2 = {'published_date': '2019-06-02 16:33:00',
                'title': 'title2',
                'href': 'link2',
                'id': 4,
                'text': 'news text 2'}

    ti_dict3 = {'published_date': '2021-06-02 15:45:00',
                'title': 'title3',
                'href': 'link3',
                'id': 5,
                'text': 'news text 3'}

    ti_list = [ti_dict1, ti_dict2, ti_dict3]

    add_ti_news_list(ti_list)

    dict1 = {'from_site': 'BusinessGazeta',
             'published_date': '2021-06-02 09:33:00',
             'title': 'Судан из-за смены власти пересмотрит соглашение с Россией о военно-морской базе',
             'href': 'https://kam.business-gazeta.ru/news/511452',
             'text': 'Судан намерен пересмотреть соглашение с Россией по ...',
             'is_match': False}

    dict2 = {'from_site': 'BusinessGazeta',
             'published_date': '2021-06-02 09:35:00',
             'title': 'Судан из-за смены власти пересмотрит соглашение с Россией о военно-морской базе',
             'href': 'link',
             'text': 'Судан намерен пересмотреть соглашение с Россией по ...',
             'is_match': True,
             'ti_id': 6}

    lst = [dict1, dict2]

    add_comp_news_list(lst)

    print(get_all_ti_news(time1))
    print(get_all_ti_news())