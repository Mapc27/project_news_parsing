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


engine = create_engine(f'sqlite:///{DATABASE_NAME}', echo=True)
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
    time = Column(DateTime, default=None)
    title = Column(String, default=None)
    text = Column(String, default=None)
    match = relationship("CompetitorsNews", backref=backref("matching_news"))

    def __repr__(self):
        return f"{self.id} | {self.time} | {self.title}"


class CompetitorsNews(Base):
    __tablename__ = "competitors_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, default=None)
    title = Column(String, default=None)
    link = Column(String, default=None)
    is_match = Column(Boolean, default=False)
    matching_news_id = Column(Integer, ForeignKey("ti_news.id"), default=None)
    website_id = Column(Integer, ForeignKey("website.id"), default=None)

    def __repr__(self):
        if self.is_match:
            return f"{self.id} | link: {self.link} |is match: {self.is_match} | matching news: {self.matching_news.title}"
        return f"{self.id} | link: {self.link} | is match: {self.is_match}"


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


def get_ti_news(session, time_: datetime, title_: str):
    news = session.query(TINews).filter(and_(TINews.time == time_, TINews.title == title_)).first()
    return news


def ti_news_exists(session, time_: datetime, title_: str) -> bool:
    return get_ti_news(session, time_, title_) is not None


def add_ti_news(time_: datetime, title_: str, text_: str):
    with get_session_without_expire() as session:
        if not ti_news_exists(session, time_, title_):
            ti_news = TINews(time=time_, title=title_, text=text_)
            session.add(ti_news)


def add_website(session, website):
    website = Website(name_website=website)
    session.add(website)
    return website


def get_website_id(session, name_website_: str):
    website = session.query(Website).filter_by(name_website=name_website_).first()
    # if website is not None:
    #     return website.id
    # return add_website(session, name_website_).id

    return website.id


def get_competitor_news(session, link):
    news = session.query(CompetitorsNews).filter(CompetitorsNews.link == link).first()
    return news


def competitor_news_exists(session, link: str):
    return get_competitor_news(session, link) is not None


def add_competitor_news(date_: datetime, title_: str, link_: str, website: str, is_match_: bool, matching_news_id_: int = None):
    with get_session() as session:
        if not competitor_news_exists(session, link_):
            website_id_ = get_website_id(session, website)
            comp_news = CompetitorsNews(time=date_,
                                        title=title_,
                                        link=link_,
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
            try:
                entry['published_date'] = datetime.fromisoformat(entry['published_date'])
            except:
                print('Incorrect date type')

        add_competitor_news(date_=entry['published_date'],
                            title_=entry['title'],
                            link_=entry['href'],
                            website=entry['from_site'],
                            is_match_=entry['is_match'],
                            matching_news_id_=entry['ti_id'])


# return ti_news id by matching
def get_matching_news_id(time_: datetime, title_: str):
    with get_session_without_expire() as session:
        news = get_ti_news(session, time_, title_)
    return news.id


def get_ti_news_for_time(before_time: datetime):
    list_ti_news = []
    with get_session_without_expire() as session:
        ti_news = session.query(TINews).filter(TINews.time < before_time).all()
        for news in ti_news:
            dic = {'time': news.time,
                   'title': news.title,
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
                 'TNV']
        for comp in comps:
            add_website(session, comp)


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()

        fill_websites()


    time1 = datetime.fromisoformat("2021-10-20")
    time2 = datetime.fromisoformat("2021-10-20")
    time3 = datetime.fromisoformat("2021-10-20")

    add_ti_news(time1, 'title1', 'text1')
    add_ti_news(time2, 'title1', 'text1')
    add_ti_news(time3, 'title2', 'text2')


    time4 = datetime.fromisoformat("2021-10-24")
    time5 = datetime.fromisoformat("2021-10-25")

    dict1 = {'from_site': 'BusinessGazeta',
             'published_date': '2021-06-02 09:33:00',
             'title': 'Судан из-за смены власти пересмотрит соглашение с Россией о военно-морской базе',
             'href': 'https://kam.business-gazeta.ru/news/511452',
             'text': 'Судан намерен пересмотреть соглашение с Россией по ...' ,
             'is_match': False}

    dict2 = {'from_site': 'BusinessGazeta',
             'published_date': '2021-06-02 09:35:00',
             'title': 'Судан из-за смены власти пересмотрит соглашение с Россией о военно-морской базе',
             'href': 'link',
             'text': 'Судан намерен пересмотреть соглашение с Россией по ...',
             'is_match': True,
             'ti_id': 2}

    lst = [dict1, dict2]

    add_comp_news_list(lst)
