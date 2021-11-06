import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwCryptoItem


class MwCryptoSpider(scrapy.Spider):
    '''
    Spider for MarketWatch cryptocurrency ticker data.
    name :  'mw_cryptos'
    '''
    name = "mw_cryptos"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/crypto-currencies"]

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
            loader.add_xpath('country_name', './/td[3]/text()')
            loader.add_xpath('industry', './/td[4]/text()')
            # sec_link = crypto.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].getall():
                yield response.follow(next_page, callback=self.parse)
