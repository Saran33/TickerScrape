# Define your item pipelines here
#
# Add pipelines to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter

from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem
from TickerScrape.models import db_connect, create_table, Security, AssetClass, Country, Currency, Industry, Exchange, Tag  # create_output_table
from TickerScrape.items import TestItem
import logging
import pandas as pd
from fuzzywuzzy import process, fuzz


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
        tag = Tag()
        security.name = item["sec_name"]
        security.ticker = item["ticker"]

        if "sec_summary" in item:
            security.summary = item["sec_summary"]
        if "sec_beta" in item:
            security.beta = item["sec_beta"]
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
            security.debt_to_equity = item["debt_to_eq"]
        if "debt_to_ass" in item:
            security.debt_to_assets = item["debt_to_ass"]
        if "current_ratio" in item:
            security.current_ratio = item["current_ratio"]
        if "quick_ratio" in item:
            security.quick_ratio = item["quick_ratio"]
        if "cash_ratio" in item:
            security.cash_ratio = item["cash_ratio"]
        if "sec_summary" in item:
            security.sec_summary = item["sec_summary"]
        if "average_rec" in item:
            security.average_rec = item["average_rec"]
        if "no_of_ratings" in item:
            security.no_of_ratings = item["no_of_ratings"]
        if "high_target" in item:
            security.high_target = item["high_target"]
        if "median_target" in item:
            security.median_target = item["median_target"]
        if "low_target" in item:
            security.low_target = item["low_target"]
        if "avg_target" in item:
            security.avg_target = item["avg_target"]

        asset_class = AssetClass(name=item["asset_class"])
        # Check whether the asset class already exists in the database
        exist_ass_class = session.query(AssetClass).filter_by(
            name=asset_class.name).first()
        if exist_ass_class is not None:
            security.asset_class = exist_ass_class
        else:
            security.asset_class = asset_class

        country = Country(name=item["country_name"])
        # Check whether the country already exists in the database
        exist_country = session.query(
            Country).filter_by(name=country.name).first()
        if exist_country is not None:
            country = exist_country
        else:
            countries_df = pd.read_csv('csv_files/country_dataset.csv')

            country_row = pd.Series(dtype='object')
            country_str = country.name.replace('.', '')
            if len(country_str) < 5:
                country_row = countries_df.loc[countries_df['ISO_3166'].astype(
                    str) == (country_str)]
            if len(country_row) == 0:
                country_row = countries_df.loc[countries_df['Country'].str.contains(
                    country.name)]
            if len(country_row) > 1:
                highest = process.extractOne(
                    country.name, country_row['Country'])
                country_row = country_row.loc[country_row['Country'].str.contains(
                    highest[0])]
            if len(country_row) == 0:
                # highest = process.extractOne(country,countries_df['Country']) # scorer=fuzz.token_set_ratio
                highest = process.extractOne(
                    country.name, countries_df['Country'], scorer=fuzz.token_set_ratio)
                print("WARNING : Using fuzzy logic to predict country:",
                      highest[0])
                country_row = countries_df.loc[countries_df['Country'].str.contains(
                    highest[0])]

            country.ISO_3166 = country_row['ISO_3166'].values[0]
            country.continent = country_row['Continent'].values[0]
            country.territory = country_row['Territory'].values[0]
            country.territory_of = country_row['Territory_of'].values[0]
            country.region = country_row['Region'].values[0]
            country.econ_group = country_row['Econ_Group'].values[0]
            country.geopol_group = country_row['Geopol_group'].values[0]
            # country.geopol_group = country.geopol_group + country_row['Geopol_group'].values[0]

            security.countries.append(country)

        # Add currency for new countrie

        if exist_country is None:
            fx_codes = pd.read_csv('csv_files/ISO_4217_FX_Codes.csv')
            entity = fx_codes.loc[fx_codes['Entity'].str.contains(
                country.name, regex=False)]
            if not entity.empty:
                for index, row in entity.iterrows():
                    match_currency = entity['Currency'][index]
                    exist_currency = session.query(Currency).filter_by(
                        name=match_currency).first()
                    if exist_currency is None:
                        currency = Currency(name=match_currency)
                        match_ticker = entity['Ticker'][index]
                        if match_ticker:
                            currency.ticker = match_ticker
                        ISO_4217 = entity['ISO_4217'][index]
                        if ISO_4217:
                            currency.ISO_4217 = ISO_4217
                        minor_unit = entity['Minor_unit'][index]
                        if minor_unit:
                            currency.minor_unit = minor_unit
                        fund = entity['Fund'][index]
                        description = entity['Description'][index]
                        if description:
                            currency.description = description
                    else:
                        currency = exist_currency
                    if currency:
                        country.currencies.append(currency)

        if "industry" in item:
            industry = Industry(name=item['industry'])
            exist_industry = session.query(
                Industry).filter_by(name=industry.name).first()
            if exist_industry is not None:  # the current industry exists
                industry = exist_industry
            security.industries.append(industry)

        if "exchange" in item:
            exchange = Exchange(name=item['exchange'])
            exist_exchange = session.query(
                Exchange).filter_by(name=exchange.name).first()
            if exist_exchange is not None:  # the current exchange exists
                exchange = exist_exchange
            security.exchanges.append(exchange)

        # check whether the current Security has tags or not
        if "tags" in item:
            for tag_name in item["tags"]:
                tag = Tag(name=tag_name)
                # check whether the current tag already exists in the database
                exist_tag = session.query(Tag).filter_by(name=tag.name).first()
                if exist_tag is not None:  # the current tag exists
                    tag = exist_tag
                security.tags.append(tag)

        try:
            session.add(security)
            session.commit()

        except:
            session.rollback()
            raise

        finally:
            session.close()

        return item


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
        exist_security = session.query(Security).filter_by(
            ticker=item["ticker"]).first()
        session.close()
        if exist_security is not None:  # the current Security exists
            raise DropItem("Duplicate item found: %s" % item["ticker"])
        else:
            return item
