# ATTENTION ЭТО МОЁ ВИДЕНИЕ ПРОЕКТА. ПИШУ ЭТО ЗДЕСЬ, ЧТОБЫ НЕ ЗАБЫТЬ МЫСЛИ.
# ЕСЛИ У ВАС ЕСТЬ ПРЕДЛОЖЕНИЯ, ТО НУЖНО СООБЩАТЬ О НИХ

# Такие методы, как достать из БД n-ное количество новостей с учётом времени


from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TINews(Base):
    __tablename__ = "ti_news"
    ti_news_id = Column(Integer, primary_key=True)
    time = Column(String(30), default=None)
    title = Column(String, default=None)
    text = Column(String, default=None)
    match = relationship("CompetitorsNews", backref=backref("matching_news"))

    def __repr__(self):
        return f"{self.ti_news_id} | {self.time} | {self.title}"


class CompetitorsNews(Base):
    __tablename__ = "competitors_news"
    comp_news_id = Column(Integer, primary_key=True)
    is_match = Column(Integer, default=None)
    matching_news_id = Column(Integer, ForeignKey("ti_news.ti_news_id"), default=None)

    def __repr__(self):
        return f"{self.comp_news_id} | is match: {self.is_match} | matching news: {self.matching_news.title}"
