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
import pandas as pd

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
        if "market_cap" in item:
            security.market_cap = item["market_cap"]
        if "pe_ratio" in item:
            security.pe_ratio = item["pe_ratio"]
        if "short_int" in item:
            security.short_int = item["short_int"]
        if "price_to_sales" in item:
            security.price_to_sales = item["price_to_sales"]
        if "price_to_book" in item:
            security.price_to_book = item["price_to_book"]
        if "price_to_fcf" in item:
            security.price_to_fcf = item["price_to_fcf"]
        if "net_margin" in item:
            security.net_margin = item["net_margin"]
        if "roc" in item:
            security.roc = item["roc"]
        if "roi" in item:
            security.roi = item["roi"]
        if "debt_to_eq" in item:
            security.debt_to_eq = item["debt_to_eq"]
        if "debt_to_ass" in item:
            security.debt_to_ass = item["debt_to_ass"]
        if "current_ratio" in item:
            security.current_ratio = item["current_ratio"]
        if "quick_ratio" in item:
            security.quick_ratio = item["quick_ratio"]
        if "cash_ratio" in item:
            security.cash_ratio = item["cash_ratio"]
        if "sec_summary" in item:
            security.sec_summary = item["sec_summary"]

        asset_class = AssetClass(name=item["asset_class"])
        # Check whether the asset class already exists in the database
        exist_ass_class = session.query(AssetClass).filter_by(name=asset_class.name).first()
        if exist_ass_class is not None:  # the current topic exists
            security.asset_class = exist_ass_class
        else:
            security.asset_class = asset_class

        country = Country(name=item["country"])
        # Check whether the source already exists in the database
        exist_country = session.query(Country).filter_by(name=country.name).first()
        if exist_country is not None:  # the current author exists
            security.country = exist_country
        else:
            security.country = country

        #Add currency for new countries
        if exist_country is None:
            try:
                fx_codes = pd.read_csv('csv_files/ISO_4217_FX_Codes.csv')
                entity = fx_codes.loc[fx_codes['Entity'].str.contains(country, regex=False)]
                if entity:
                    for index, row in entity.iterrows():
                        match_currency = entity['Currency'][index]
                        exist_currency = session.query(Currency).filter_by(name=match_currency).first()
                        if exist_currency is None:
                            currency = Currency(name=match_currency)
                            match_ticker = entity['Ticker'][index]
                            if match_ticker:
                                currency.ticker = match_ticker
                            ISO_4217 = entity['ISO_4217'][index]
                            if ISO_4217:
                                currency.ISO_4217 = ISO_4217
                            minor_unit = entity['Minor unit'][index]
                            if minor_unit:
                                currency.minor_unit = match_ticker
                            fund = entity['Fund'][index]
                            print (fund)
                            description = entity['Description'][index]
                            if description:
                                currency.description = description
                        else:
                            currency = exist_currency
                        security.currency.append(currency)
                
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
            security.authors.append(author)

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
