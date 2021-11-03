import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwSecurityItem
from unicodedata import normalize
from bs4 import BeautifulSoup
import grequests


class MWStocksSpider(scrapy.Spider):
    '''
    Spider for MarketWatch stock ticker data.
    name :  'mw_stocks'
    '''
    name = "mw_stocks"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = [f"https://www.marketwatch.com/tools/markets/stocks"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        countries = response.xpath('//*[@id="marketsindex"]/ul[@class="list-unstyled"]/li/a')
        for country in countries:
                country_link = country.xpath('.//@href').get()
                request = response.follow(country_link, self.parse_country)
                if request:
                    yield request

    def parse_country(self, response):
        asset_class = response.xpath('//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        country_name = response.xpath('//*[@id="marketsindex"]/h2/text()').get()
        country_name = country_name.replace('Location: ', '')
        stocks = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for stock in stocks:
            loader = ItemLoader(item=MwSecurityItem(), selector=stock)
            loader.add_value('asset_class', asset_class)
            loader.add_value('country_name', country_name)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/td[2]/text()')
            loader.add_xpath('industry', './/td[3]/text()')
            sec_link = stock.xpath('.//a/@href').get()
            security_item = loader.load_item()
            request = response.follow(sec_link, self.parse_security, meta={'security_item': security_item})
            request.meta['security_item'] = security_item
            if request:
                yield request
            else:
                yield security_item

        # Go to next page
        if response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li[@class="active"]/span/text()').get() == '1':
            for a in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[:-1].getall():
                yield response.follow(a, callback=self.parse)


    def parse_security(self, response):
        security_item = response.meta['security_item']
        loader = ItemLoader(item=security_item, response=response)
        sec_beta = response.xpath('//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[7]/span[1]/text()').get()
        if sec_beta:
            loader.add_value('sec_beta', sec_beta)
        market_cap = response.xpath('//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[4]/span[1]/text()').get()
        if market_cap:
            loader.add_value('market_cap', market_cap)
        pe_ratio = response.xpath('//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[9]/span[1]/text()').get()
        if pe_ratio:
            loader.add_value('pe_ratio', pe_ratio)
        short_int = response.xpath('//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[14]/span[1]/text()').get()
        if short_int:
            loader.add_value('short_int', short_int)

        profile_url = response.xpath('//a[@instrument-target="company-profile"]/@href').get()
        if profile_url:
            request = response.follow(profile_url, self.parse_profile, meta={'security_item': security_item})
            request.meta['security_item'] = security_item
            if request:
                yield request
            else:
                yield loader.load_item()
        else:
            yield loader.load_item()

    def parse_profile(self, response):
        security_item = response.meta['security_item']
        loader = ItemLoader(item=security_item, response=response)
        price_to_sales = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[4]/td[2]/text()').get()
        if price_to_sales:
            loader.add_value('price_to_sales', price_to_sales)
        price_to_book = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[5]/td[2]/text()').get()
        if price_to_book:
            loader.add_value('price_to_book', price_to_book)
        price_to_fcf = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[6]/td[2]/text()').get()
        if price_to_fcf:
            loader.add_value('price_to_fcf', price_to_fcf)
        net_margin = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[4]/td[2]/text()').get()
        if net_margin:
            loader.add_value('net_margin', net_margin)
        roc = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[7]/td[2]/text()').get()
        if roc:
            loader.add_value('roc', roc)
        roi = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[8]/td[2]/text()').get()
        if roi:
            loader.add_value('roi', roi)
        debt_to_eq = response.xpath('//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[1]/td[2]/text()').get()
        if debt_to_eq:
            loader.add_value('debt_to_eq', debt_to_eq)
        debt_to_ass = response.xpath('//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[3]/td[2]/text()').get()
        if debt_to_ass:
            loader.add_value('debt_to_ass', debt_to_ass)
        current_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[1]/td[2]/text()').get()
        if current_ratio:
            loader.add_value('current_ratio', current_ratio)
        quick_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[2]/td[2]/text()').get()
        if quick_ratio:
            loader.add_value('quick_ratio', quick_ratio)
        cash_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[3]/td[2]/text()').get()
        if cash_ratio:
            loader.add_value('cash_ratio', cash_ratio)
        sec_summary = response.xpath('//p[@class="description__text"]/text()').get()
        if sec_summary:
            loader.add_value('sec_summary', sec_summary)
        yield loader.load_item()