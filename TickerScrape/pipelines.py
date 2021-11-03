# Define your item pipelines here
#
# Add pipelines to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from TickerScrape.models import Article, Tag, db_connect, create_table, Topic, Source, Author, SnipBlob, Blob, SnipVader, Vader #  create_output_table
from TickerScrape.items import clean_text, extract_standfirst, TestItem
import logging

class SaveArticlesPipeline(object):
    def __init__(self, stats):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.stats)

    def process_item(self, item, spider):
        self.stats.inc_value('typecount/%s' % type(item).__name__)
        # spider.crawler.stats.inc_value('scraped_items')
        self.stats.inc_value('scraped_items')

        if isinstance(item, TestItem):
            return item
        else:
            return self.process_article(item, spider)

    def process_article(self, item, spider):
        """Save articles in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        article = Article()
        topic = Topic()
        source = Source()
        author = Author()
        tag = Tag()
        snip_blob = SnipBlob()
        blob = Blob()
        snip_vader = SnipVader()
        vader = Vader()
        article.published_date = item["published_date"]
        article.headline = item["headline"]

        sf_list = []
        for sf_str in item["standfirst"]:
            sf_str = extract_standfirst(sf_str)
            sf_list.append(sf_str)
        sf = ' '.join(sf_list)
        sf = clean_text(sf)
        article.standfirst = sf
        # article.standfirst = item["standfirst"]

        if "article_summary" in item:
            article.summary = item["article_summary"]
        if "image_caption" in item:
            article.image_caption = item["image_caption"]
        if "article_content" in item:
            article.content = item["article_content"]
        if "article_footnote" in item:
            article.footnote = item["article_footnote"]
        article.article_link = item["article_link"]
        if "origin_link" in item:
            article.origin_link = item["origin_link"]

        topic = Topic(name=query.capitalize())
        # Check whether the topic already exists in the database
        exist_topic = session.query(Topic).filter_by(name=topic.name).first()
        if exist_topic is not None:  # the current topic exists
            topic = exist_topic
        article.topics.append(topic)

        source.name = spider.name
        # Check whether the source already exists in the database
        exist_source = session.query(Source).filter_by(name=source.name).first()
        if exist_source is not None:  # the current author exists
            article.source = exist_source
        else:
            article.source = source

        #check whether the current article has authors or not
        if "authors" in item:
            try:
                for author_name, auth in item["authors"].items():
                    author = Author(name=author_name)
                    # author.name = auth['author_name']
                    if 'author_position' in auth:
                        author.position = auth['author_position']
                    if "author_bio" in auth:
                        author.bio = auth["author_bio"]
                    if "bio_link" in auth:
                        author.bio_link = auth["bio_link"]
                    if "author_twitter" in auth:
                        author.twitter = auth["author_twitter"]
                    if "author_fb" in auth:
                        author.facebook = auth["author_fb"]
                    if "author_email" in auth:
                        author.email = auth["author_email"]
                    if "author_bias" in auth:
                        author.bias = auth["author_bias"]
                    if "author_birthday" in auth:
                        author.birthday = auth["author_birthday"]
                    if "author_bornlocation" in auth:
                        author.bornlocation = auth["author_bornlocation"]
            except:
                for a in item["authors"]:
                    for author_name, auth in a.items():
                        author = Author(name=author_name)
                    if 'author_position' in auth:
                        author.position = auth['author_position']
                    if "author_bio" in auth:
                        author.bio = auth["author_bio"]
                    if "bio_link" in auth:
                        author.bio_link = auth["bio_link"]
                    if "author_twitter" in auth:
                        author.twitter = auth["author_twitter"]
                    if "author_linkedin" in auth:
                        author.linkedin = auth["author_linkedin"]
                    if "author_fb" in auth:
                        author.facebook = auth["author_fb"]
                    if "author_email" in auth:
                        author.email = auth["author_email"]
                    if "author_bias" in auth:
                        author.bias = auth["author_bias"]
                    if "author_birthday" in auth:
                        author.birthday = auth["author_birthday"]
                    if "author_bornlocation" in auth:
                        author.bornlocation = auth["author_bornlocation"]
            # check whether the author exists
            exist_author = session.query(Author).filter_by(name=author.name).first()
            if exist_author is not None:  # the current author exists
                author = exist_author
            article.authors.append(author)

        # check whether the current article has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name=tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                article.tags.append(tag)

        # Add sentiment scores
        head = article.headline
        sf = article.standfirst
        # head = item["headline"]
        # sf = sf
        text = ' — ...'.join([head, sf])
        # print("TEXT:", text)

        snip_blob = SnipBlob()

        subjectivity_score = self.get_subjectivity(text)
        snip_blob.subjectivity = subjectivity_score
        polarity_score = self.get_polarity(text)
        snip_blob.polarity = polarity_score

        snip_vader = SnipVader()
        # SIA = 0
        SIA = self.get_SIA(text)
        compound = (SIA['compound'])
        neg = (SIA['neg'])
        neu = (SIA['neu'])
        pos = (SIA['pos'])
        snip_vader.compound = compound
        snip_vader.negative = neg
        snip_vader.neutral = neu
        snip_vader.positive = pos

        article.snip_blob = snip_blob
        article.snip_vader = snip_vader

        try:
            session.add(article)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item

    # Get the subjectivity
    def get_subjectivity(self, text):
        """
        Returns a subjectivity score between 0 and 1.
        0 is objective and 1 is subjective.
        """
        return TextBlob(text).sentiment.subjectivity

    # Get the polarity
    def get_polarity(self, text):
        """
        Returns a polarity score between -1 and 1.
        -1 is negative sentiment and 1 is positive sentiment.
        """
        return TextBlob(text).sentiment.polarity

    # Get the sentiment scores
    def get_SIA(self, text):
        sia = SentimentIntensityAnalyzer()
        sentiment = sia.polarity_scores(text)
        return sentiment


class DuplicatesPipeline(object):

    def __init__(self):
        """
        Initializes database connection and sesssionmaker.
        Creates tables.
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("****DuplicatesPipeline: database connected****")

    def process_item(self, item, spider):
        if isinstance(item, TestItem):
            return item
        else:
            return self.process_article(item, spider)

    def process_article(self, item, spider):
        session = self.Session()
        exist_article = session.query(Article).filter_by(article_link=item["article_link"]).first()
        session.close()
        if exist_article is not None:  # the current article exists
            topic_name = query.capitalize()
            # if topic_name in exist_article.topics:
            exist_topic = session.query(Topic).filter_by(name=topic_name).first()
            if exist_topic is not None:  # the current topic exists
                raise DropItem("Duplicate item found: %s" % item["headline"])
            else:
                article = exist_article
                article.topics.append(topic_name)
                raise DropItem("Duplicate item found: %s" % item["headline"])
        else:
            return item
