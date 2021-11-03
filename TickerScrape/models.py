from sqlalchemy import create_engine, Column, Table, ForeignKey, MetaData
from sqlalchemy.orm import relationship  # , foreign
from sqlalchemy.ext.declarative import declarative_base  # DeclarativeBase
from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text)
from scrapy.utils.project import get_project_settings
# from sqlalchemy.pool import StaticPool

Base = declarative_base()

#CONNECTION_STRING = 'sqlite:///FiScrape.db'


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


# Association Table for Many-to-Many relationship between Article and Author
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many
authors_association = Table('authors_association', Base.metadata,
                            Column('article_id', Integer, ForeignKey(
                                'article.id'), primary_key=True),
                            Column('author_id', Integer, ForeignKey(
                                'author.id'), primary_key=True)
                            )

# Association Table for Many-to-Many relationship between Article and Topic
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many
topics_association = Table('topics_association', Base.metadata,
                           Column('article_id', Integer, ForeignKey(
                               'article.id'), primary_key=True),
                           Column('topic_id', Integer, ForeignKey(
                               'topic.id'), primary_key=True)
                           )

# Association Table for Many-to-Many relationship between Article and Tag
# https://docs.sqlalchemy.org/en/13/orm/basic_relationships.html#many-to-many
tags_association = Table('tags_association', Base.metadata,
                         Column('article_id', Integer, ForeignKey(
                             'article.id'), primary_key=True),
                         Column('tag_id', Integer, ForeignKey(
                             'tag.id'), primary_key=True)
                         )


class Article(Base):
    __tablename__ = "article"

    id = Column(Integer, primary_key=True)
    published_date = Column('published_date', DateTime)
    headline = Column('headline', Text(), nullable=False)
    standfirst = Column('standfirst', Text())
    summary = Column('summary', Text(), default=None)
    image_caption = Column('image_caption', Text(), default=None)
    content = Column('content', Text(), default=None)
    footnote = Column('footnote', Text(), default=None)
    article_link = Column('article_link', Text())
    origin_link = Column('origin_link', Text())
    # , nullable=False)  # Many articles to one source
    source_id = Column(Integer, ForeignKey('source.id'))
    #source = relationship('Source', backref='articles', nullable=False)
    authors = relationship('Author', secondary='authors_association',
                           lazy='dynamic', backref="article", overlaps="article,authors")  # M-to-M for article and authors
    topics = relationship('Topic', secondary='topics_association',
                          lazy='dynamic', backref="article", overlaps="article,topics")  # M-to-M for article and topic
    tags = relationship('Tag', secondary='tags_association',
                        lazy='dynamic', backref="article", overlaps="article,tags")  # M-to-M for article and tag
    # 1-to-1 for article and snip_blob
    snip_blob = relationship(
        'SnipBlob', back_populates='article', uselist=False)
    blob = relationship('Blob', back_populates='article',
                        uselist=False)  # 1-to-1 for article and blob
    # 1-to-1 for article and snip_vader
    snip_vader = relationship(
        'SnipVader', back_populates='article', uselist=False)
    vader = relationship('Vader', back_populates='article',
                         uselist=False)  # 1-to-1 for article and vader
    # def __repr__(self):
    #     return "<{0} Id: {1} - Published: {2} Headline: {3} Standfirst: {4} Source_id: {5} URL: {6}>".format(self.__class__name, self.id,
    #             self.published_date, self.headline, self.standfirst, self.link)


class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)  # , nullable=False)
    articles = relationship('Article', secondary='topics_association',
                            lazy='dynamic', backref="topic", overlaps="article,topics")  # M-to-M for article and topic
    # def __repr__(self):
    #     return "<{0} Id: {1} - Topic: {2} Headline: {3}>".format(self.__class__name, self.id,
    #             self.name)


class Source(Base):
    __tablename__ = "source"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True)  # , nullable=False)
    inception = Column('inception', DateTime, default=None)
    location = Column('location', String(150), default=None)
    about = Column('about', Text(), default=None)
    # Add https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B2%5D=2&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&field_news_bias_nid_1%5B4%5D=4&title=
    bias = Column('bias', Text(), default=None)
    # One author to many Articles
    articles = relationship('Article', backref='source', lazy='dynamic')

    def __repr__(self):
        # return "<{0} Id: {1} - Name: {2} Bias: {6} About: {5}>".format(self.__class__name, self.id,
        #         self.name, self.bias, self.about)
        return "<{0} Id: {1} - Name: {2}>".format(self.__tablename__, self.id,
                                                  self.name)


class Author(Base):
    __tablename__ = "author"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(50), unique=True, default=None)
    position = Column('position', String(150), default=None)
    bio = Column('bio', Text(), default=None)
    bio_link = Column('bio_link', Text(), default=None)
    email = Column('email', String(50), default=None)
    twitter = Column('twitter', String(36), default=None)
    linkedin = Column('linkedin', String(36), default=None)
    facebook = Column('facebook', String(36), default=None)
    birthday = Column('birthday', DateTime, default=None)
    bornlocation = Column('bornlocation', String(150), default=None)
    articles = relationship('Article', secondary='authors_association',
                            lazy='dynamic', backref="author", overlaps="article,authors")  # M-to-M for article and authors
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2} Bio: {3} Twitter: {4} Email: {5}>".format(self.__class__name, self.id,
    #             self.name, self.twitter, self.email)
    # __table__args = {'exted_existing':True}
    # bias = Column('bias', Text()) # Add https://www.allsides.com/media-bias/media-bias-ratings?field_featured_bias_rating_value=All&field_news_source_type_tid%5B1%5D=1&field_news_bias_nid_1%5B1%5D=1&field_news_bias_nid_1%5B2%5D=2&field_news_bias_nid_1%5B3%5D=3&field_news_bias_nid_1%5B4%5D=4&title=


class Tag(Base):
    __tablename__ = "tag"

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True, default=None)
    articles = relationship('Article', secondary='tags_association',
                            lazy='dynamic', backref="tag")  # , overlaps="article,tags")  # M-to-M for article and tag
    # def __repr__(self):
    #     return "<{0} Id: {1} - Name: {2}>".format(self.__class__name, self.id,
    #             self.name)


class SnipBlob(Base):
    __tablename__ = "snip_blob"  # Blob sentiment scores for the headline and standfirst
    # TextBlob, based on the Natural Language ToolKit (NLTK), sentiment scores.

    id = Column(Integer, primary_key=True)
    subjectivity = Column('subjectivity', Float, default=None)
    polarity = Column('polarity', Float, default=None)
    # article = relationship('Article', uselist=False, backref='snip_blob')  # One SnipBlob to one Article
    # 1-to-1 for article and snip_blob
    article_id = Column(Integer, ForeignKey('article.id'), unique=True)
    article = relationship(
        "Article", back_populates="snip_blob", uselist=False)
#     def __repr__(self):
#         # return "<{0} Id: {1} - Name: {2} Bias: {6} About: {5}>".format(self.__class__name, self.id,
#         #         self.name, self.bias, self.about)
#         return "<{0} Id: {1} - Subjectivity: {2} Polarity: {3} Article Id: {4}>".format(self.__class__name, self.id,
#                 self.subjectivity, self.polarity, self.article.id)


class Blob(Base):
    __tablename__ = "blob"  # TextBlob sentiment scores for the main body
    # TextBlob, based on the Natural Language ToolKit (NLTK), sentiment scores.

    id = Column(Integer, primary_key=True)
    subjectivity = Column('subjectivity', Float, default=None)
    polarity = Column('polarity', Float, default=None)
    article_id = Column(Integer, ForeignKey('article.id'),
                        unique=True)  # One Blob to one Article
    article = relationship("Article", back_populates="blob", uselist=False)
#     def __repr__(self):
#         # return "<{0} Id: {1} - Name: {2} Bias: {6} About: {5}>".format(self.__class__name, self.id,
#         #         self.name, self.bias, self.about)
#         return "<{0} Id: {1} - Subjectivity: {2} Polarity: {3} Article Id: {4}>".format(self.__class__name, self.id,
#                 self.subjectivity, self.polarity,self.article.id)


class SnipVader(Base):
    __tablename__ = "snip_vader"  # Vader sentiment scores for the headline and standfirst
    # Valence Aware Dictionary and sEntiment Reasoning lexicon-based sentiment scores

    id = Column(Integer, primary_key=True)
    compound = Column('compound', Float, default=None)
    negative = Column('negative', Float, default=None)
    neutral = Column('neutral', Float, default=None)
    positive = Column('positive', Float, default=None)
    article_id = Column(Integer, ForeignKey('article.id'),
                        unique=True)  # One SnipVader to one Article
    article = relationship(
        "Article", back_populates="snip_vader", uselist=False)
#     def __repr__(self):
#         # return "<{0} Id: {1} - Name: {2} Bias: {6} About: {5}>".format(self.__class__name, self.id,
#         #         self.name, self.bias, self.about)
#         return "<{0} Id: {1} - Compound: {2} Negative: {3} Neutral: {4} Positive: {5} Article Id: {6}>".format(self.__class__name, self.id,
#                 self.compound, self.negative, self.neutral, self.positive, self.article.id)


class Vader(Base):
    __tablename__ = "vader"  # Vader sentiment scores for the main body
    # Valence Aware Dictionary and sEntiment Reasoning lexicon-based sentiment scores

    id = Column(Integer, primary_key=True)
    compound = Column('compound', Float, default=None)
    negative = Column('negative', Float, default=None)
    neutral = Column('neutral', Float, default=None)
    positive = Column('positive', Float, default=None)
    article_id = Column(Integer, ForeignKey('article.id'),
                        unique=True)  # One Vader to one Article
    article = relationship("Article", back_populates="vader", uselist=False)
#     def __repr__(self):
#         # return "<{0} Id: {1} - Name: {2} Bias: {6} About: {5}>".format(self.__class__name, self.id,
#         #         self.name, self.bias, self.about)
#         return "<{0} Id: {1} - Compound: {2} Negative: {3} Neutral: {4} Positive: {5} Article Id: {6}>".format(self.__class__name, self.id,
#                 self.compound, self.negative, self.neutral, self.positive, self.article.id)

# from sqlalchemy.orm import aliased
# Sentiment = aliased(SnipVader)
