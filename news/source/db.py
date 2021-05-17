# Такие методы, как достать из БД n-ное количество новостей с учётом времени

from contextlib import contextmanager

from sqlalchemy import (Column,
                        Integer,
                        String,
                        ForeignKey,
                        create_engine,
                        and_,
                        exc,)
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os

DATABASE_NAME = 'parsed_news.sqlite'

import os


engine = create_engine(f'sqlite:///{DATABASE_NAME}')
Session = sessionmaker(bind=engine)

Base = declarative_base()


class TINews(Base):
    __tablename__ = "ti_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(String(30), default=None)
    title = Column(String, default=None)
    text = Column(String, default=None)
    match = relationship("CompetitorsNews", backref=backref("matching_news"))

    def __repr__(self):
        return f"{self.id} | {self.time} | {self.title}"


class CompetitorsNews(Base):
    __tablename__ = "competitors_news"
    id = Column(Integer, primary_key=True, autoincrement=True)
    link = Column(String, default=None)
    is_match = Column(Integer, default=None)
    matching_news_id = Column(Integer, ForeignKey("ti_news.id"), default=None)

    def __repr__(self):
        return f"{self.id} | is match: {self.is_match} | matching news: {self.matching_news.title}"


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


def add_ti_news(time_:str, title_: str, text_: str):
    with get_session_without_expire() as session:
        ti_news = TINews(time=time_, title=title_, text=text_)
        session.add(ti_news)


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()

    session = Session()

