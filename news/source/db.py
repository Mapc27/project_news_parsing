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
    link = Column(String, default=None)
    is_match = Column(Boolean, default=None)
    matching_news_id = Column(Integer, ForeignKey("ti_news.id"), default=None)

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


def get_competitor_news(session, link):
    news = session.query(CompetitorsNews).filter(CompetitorsNews.link == link).first()
    return news


def competitor_news_exists(session, link: str):
    return get_competitor_news(session, link) is not None


def add_competitor_news(link_: str, is_match_: bool, matching_news_id_: int = None):
    with get_session() as session:
        if not competitor_news_exists(session, link_):
            comp_news = CompetitorsNews(link=link_,
                                        is_match=is_match_,
                                        matching_news_id=matching_news_id_)
            if is_match_:
                matching_news_ = session.query(TINews).get(matching_news_id_)
                comp_news.matching_news = matching_news_
            session.add(comp_news)


if __name__ == '__main__':
    db_is_created = os.path.exists(DATABASE_NAME)
    if not db_is_created:
        create_db()

    add_ti_news('time1', 'title1', 'text1')
    add_ti_news('time1', 'title1', 'text1')
    add_ti_news('time2', 'title2', 'text2')


