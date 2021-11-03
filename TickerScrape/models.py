from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship  # , foreign
from sqlalchemy.ext.declarative import declarative_base  # DeclarativeBase
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
# from sqlalchemy.pool import StaticPool

Base = declarative_base()

# CONNECTION_STRING = 'sqlite:///TickerScrape.db'


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"),
                         connect_args={'check_same_thread': False},)
                        #  poolclass=StaticPool)  # , echo=True)
    # return create_engine(get_project_settings().get("CONNECTION_STRING"), connect_args={'check_same_thread': False})


def create_table(engine):
    Base.metadata.create_all(engine)

# def create_output_table(engine, spider_name):
#     # Create table with the spider_name
#     DeclarativeBase.metadata.create_all(engine)


# Association Table for Many-to-Many relationship between Security and Country
countries_association = Table('countries_association', Base.metadata,
                            Column('security_id', Integer, ForeignKey(
                                'security.id'), primary_key=True),
                            Column('country_id', Integer, ForeignKey(
                                'country.id'), primary_key=True)
                            )

# Association Table for Many-to-Many relationship between Security and Sector
industries_association = Table('industries_association', Base.metadata,
                           Column('security_id', Integer, ForeignKey(
                               'security.id'), primary_key=True),
                           Column('industry_id', Integer, ForeignKey(
                               'industry.id'), primary_key=True)
                           )

# Association Table for Many-to-Many relationship between Security and Exchange
exchanges_association = Table('exchanges_association', Base.metadata,
                         Column('security_id', Integer, ForeignKey(
                             'security.id'), primary_key=True),
                         Column('exchange_id', Integer, ForeignKey(
                             'exchange.id'), primary_key=True)
                         )

# Association Table for Many-to-Many relationship between Security and Tag
tags_association = Table('tags_association', Base.metadata,
                         Column('security_id', Integer, ForeignKey(
                             'security.id'), primary_key=True),
                         Column('tag_id', Integer, ForeignKey(
                             'tag.id'), primary_key=True)
                         )

class Security(Base):
    __tablename__ = "security"

    id = Column(Integer, primary_key=True)
    ticker = Column('ticker', Text(), nullable=False)
    name = Column('name', Text())
    industry = Column('industry', Text(), default=None)
    beta = Column('beta', Float, default=None)
    average_rec = Column('average_rec', Text(), default=None)
    market_cap = Column('market_cap', Float, default=None)
    pe_ratio = Column('pe_ratio', Float, default=None)
    short_int = Column('short_int', Float, default=None)
    price_to_sales = Column('price_to_sales', Float, default=None)
    price_to_book = Column('price_to_book', Float, default=None)
    price_to_fcf = Column('price_to_fcf', Float, default=None)
    net_margin = Column('net_margin', Float, default=None)
    roc = Column('roc', Float, default=None)
    roi = Column('roi', Float, default=None)
    debt_to_equity = Column('debt_to_equity', Float, default=None)
    debt_to_assets = Column('debt_to_assets', Float, default=None)
    current_ratio = Column('current_ratio', Float, default=None)
    quick_ratio = Column('quick_ratio', Float, default=None)
    cash_ratio = Column('cash_ratio', Float, default=None)
    summary = Column('summary', Text(), default=None)
    inception_date = Column('inception_date', DateTime, default=None)
    # Many securities to one asset class
    asset_class_id = Column(Integer, ForeignKey('asset_class.id'))
    countries = relationship('Country', secondary='countries_association',
                           lazy='dynamic', backref="security", overlaps="security,countries")  # M-to-M for securities and countries
    industries = relationship('Industry', secondary='industries_association',
                          lazy='dynamic', backref="security", overlaps="security,industries")  # M-to-M for security and topic
    exchanges = relationship('Exchange', secondary='exchanges_association',
                        lazy='dynamic', backref="security", overlaps="security,exchanges")  # M-to-M for security and tag
    # 1-to-1 for security and signal
    signal = relationship(
        'Signal', back_populates='security', uselist=False)
    # def __repr__(self):
    #     return "<{0} Id: {1} - Ticker: {2}, Name: {3}, Industry: {4} Beta: {5} Analyst Rec: {6} Mkt. Cap: {7}>".format(self.__class__name, self.id,
    #             self.ticker, self.name, self.industry, self.beta, self.average_rec, self.market_cap)

class AssetClass(Base):
    __tablename__ = "asset_class"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(150), unique=True)
    securities = relationship('security', backref='asset_class', lazy='dynamic')

    def __repr__(self):
        # return "<{0} Id: {1} - Name: {2}>".format(self.__class__name, self.id,
        #         self.name)
        return "<{0} Id: {1} - Name: {2}>".format(self.__tablename__, self.id,
                                                  self.name)

class Country(Base):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)  # , nullable=False)
    continent = Column('continent', String(30), default=None)
    region = Column('region', String(30), default=None)
    geo_market = Column('geo_market', String(30), default=None)
    currency_id = Column(Integer, ForeignKey('currency.id'))
    cb_on_rate = Column('cb_on_rate', Float, default=None)
    last_rate_change = Column('last_rate_change', DateTime, default=None)
    last_m_infl = Column('last_m_infl', Float, default=None)
    gdp = Column('gdp', Float, default=None)
    gnp = Column('gnp', Float, default=None)
    securities = relationship('security', secondary='countries_association',
                            lazy='dynamic', backref="country", overlaps="security,countries")  # M-to-M for security and topic
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2} Continent: {3}, Region: {4}, Geopol. Group: {5}>".format(self.__class__name, self.id,
    #             self.name, self.continent, self.region, self.geo_region)


class Currency(Base):
    __tablename__ = "currency"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(150), unique=True)
    ticker = Column('ticker', String(50), unique=True)
    countries = relationship('country', backref='currency', lazy='dynamic')
    exchanges = relationship('exchange', backref='currency', lazy='dynamic')

    def __repr__(self):
        # return "<{0} Id: {1} - Name: {2} Ticker: {3}>".format(self.__class__name, self.id,
        #         self.name, self.ticker)
        return "<{0} Id: {1} - Name: {2}>".format(self.__tablename__, self.id,
                                                  self.name)


class Industry(Base):
    __tablename__ = "industry"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True, default=None)
    sector = Column('sector', Text(), default=None)
    beta = Column('beta', Float, default=None)
    market_cap = Column('market_cap', Float, default=None)
    pe_ratio = Column('pe_ratio', Float, default=None)
    price_to_sales = Column('price_to_sales', Float, default=None)
    price_to_book = Column('price_to_book', Float, default=None)
    price_to_fcf = Column('price_to_fcf', Float, default=None)
    net_margin = Column('net_margin', Float, default=None)
    roc = Column('roc', Float, default=None)
    roi = Column('roi', Float, default=None)
    debt_to_equity = Column('debt_to_equity', Float, default=None)
    debt_to_assets = Column('debt_to_assets', Float, default=None)
    current_ratio = Column('current_ratio', Float, default=None)
    quick_ratio = Column('quick_ratio', Float, default=None)
    cash_ratio = Column('cash_ratio', Float, default=None)
    securities = relationship('security', secondary='industries_association',
                            lazy='dynamic', backref="industry", overlaps="security,industries")  # M-to-M for security and authors
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2} Sector: {3} Beta: {4} Mkt. Cap: {5}>".format(self.__class__name, self.id,
    #             self.name, self.sector, self.market_cap)
    # __table__args = {'exted_existing':True}

class Exchange(Base):
    __tablename__ = "exchange"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)  # , nullable=False)
    country_id = Column(Integer, ForeignKey('country.id'))
    timezone = Column(String(150), unique=True, default=None)
    securities = relationship('security', secondary='exchanges_association',
                            lazy='dynamic', backref="exchange", overlaps="security,exchanges")  # M-to-M for security and topic
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2} country_id: {3}>".format(self.__class__name, self.id,
    #             self.name, self.country_id)

class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True, default=None)
    securities = relationship('security', secondary='tags_association',
                            lazy='dynamic', backref="tag")  # , overlaps="security,tags")  # M-to-M for security and tag
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2}>".format(self.__class__name, self.id,
    #             self.name)

# from sqlalchemy.orm import aliased
# Sector = aliased(Industry)
