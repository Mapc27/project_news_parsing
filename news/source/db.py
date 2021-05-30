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
    time = Column(String, default=None)
    title = Column(String, default=None)
    text = Column(String, default=None)
    match = relationship("CompetitorsNews", backref=backref("matching_news"))

    def __repr__(self):
        return f"{self.id} | {self.time} | {self.title}"


class CompetitorsNews(Base):
    __tablename__ = "competitors_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
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


def get_ti_news(session, time_: str, title_: str):
    news = session.query(TINews).filter(and_(TINews.time == time_, TINews.title == title_)).first()
    return news


def ti_news_exists(session, time_: str, title_: str) -> bool:
    return get_ti_news(session, time_, title_) is not None


def add_ti_news(time_: str, title_: str, text_: str):
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
    if website is not None:
        return website.id
    return add_website(session, name_website_).id


def get_competitor_news(session, link):
    news = session.query(CompetitorsNews).filter(CompetitorsNews.link == link).first()
    return news


def competitor_news_exists(session, link: str):
    return get_competitor_news(session, link) is not None


def add_competitor_news(link_: str, website: str, is_match_: bool, matching_news_id_: int = None):
    with get_session() as session:
        if not competitor_news_exists(session, link_):
            website_id_ = get_website_id(session, website)
            comp_news = CompetitorsNews(link=link_,
                                        is_match=is_match_,
                                        matching_news_id=matching_news_id_,
                                        website_id=website_id_)
            if is_match_:
                matching_news_ = session.query(TINews).get(matching_news_id_)
                comp_news.matching_news = matching_news_
            session.add(comp_news)


# return ti_news id by matching
def get_matching_news_id(time_: str, title_: str):
    with get_session_without_expire() as session:
        news = get_ti_news(session, time_, title_)
    return news.id


def get_ti_news_for_time(before_time: str):
    list_ti_news = []
    with get_session_without_expire() as session:
        ti_news = session.query(TINews).filter(TINews.time < before_time).all()
        for news in ti_news:
            dic = {'time': news.time,
                   'title': news.title,
                   'text': news.text}
            list_ti_news.append(dic)

    return list_ti_news


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()

    add_ti_news('time1', 'title1', 'text1')
    add_ti_news('time1', 'title1', 'text1')
    add_ti_news('time2', 'title2', 'text2')

    add_competitor_news('link6', 'website', True, 2)
    add_ti_news('time3', 'title2', 'text2')

    print(get_ti_news_for_time('time3'))


