import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwCryptoItem
from TickerScrape.ticker_tools import extract_bond_country


class MwCryptoSpider(scrapy.Spider):
    '''
    Spider for MarketWatch cryptocurrency ticker data.
    name :  'mw_cryptos'
    '''
    name = "mw_cryptos"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = [
        "https://www.marketwatch.com/tools/markets/crypto-currencies"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        cryptos = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for crypto in cryptos:
            loader = ItemLoader(item=MwCryptoItem(), selector=crypto)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            country_name = response.xpath('.//td[3]/text()').get()
            country_name = extract_bond_country(country_name)
            if country_name:
                loader.add_value('country_name', country_name)
            loader.add_xpath('industry', './/td[4]/text()')
            # sec_link = crypto.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            pages = response.xpath(
                '//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href').getall()
            if pages:
                next_page = None
                try:
                    next_page = pages[-1]
                except:
                    pass
                if next_page:
                    yield response.follow(next_page, callback=self.parse)
