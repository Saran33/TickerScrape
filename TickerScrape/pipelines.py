# Define your item pipelines here
#
# Add pipelines to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from TickerScrape.models import db_connect, create_table, Security, AssetClass, Country, Currency, Industry, Tag #  create_output_table
from TickerScrape.items import clean_text, extract_standfirst, TestItem
import logging

class SaveSecuritiesPipeline(object):
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
            return self.process_security(item, spider)

    def process_security(self, item, spider):
        """Save Securitys in the database
        This method is called for every item pipeline component
        """
        session = self.Session()
        security = Security()
        asset_class = AssetClass()
        country = Country()
        currency = Currency()
        industry = Industry()
        tag = Tag()
        security.name = item["sec_name"]
        security.ticker = item["ticker"]

        if "industry" in item:
            security.industry = item["industry"]
        if "sec_summary" in item:
            security.summary = item["sec_summary"]
        if "sec_beta" in item:
            security.beta = item["sec_beta"]
        if "average_rec" in item:
            security.average_rec = item["average_rec"]
        if "sec_market_cap" in item:
            security.origin_link = item["sec_market_cap"]

        asset_class.name = item["asset_class"]
        # Check whether the asset class already exists in the database
        exist_ass_class = session.query(AssetClass).filter_by(name=asset_class.name).first()
        if exist_ass_class is not None:  # the current topic exists
            topic = exist_ass_class
        Security.topics.append(topic)

        country.name = item["country"]
        # Check whether the source already exists in the database
        exist_source = session.query(Source).filter_by(name=source.name).first()
        if exist_source is not None:  # the current author exists
            Security.source = exist_source
        else:
            Security.source = source

        #check whether the current Security has authors or not
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
            Security.authors.append(author)

        # check whether the current Security has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name=tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                Security.tags.append(tag)


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
            return self.process_security(item, spider)

    def process_security(self, item, spider):
        session = self.Session()
        exist_security = session.query(Security).filter_by(ticker=item["ticker"]).first()
        session.close()
        if exist_security is not None:  # the current Security exists
            raise DropItem("Duplicate item found: %s" % item["headline"])
        else:
            return item
