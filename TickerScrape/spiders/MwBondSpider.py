import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwBondItem
from TickerScrape.ticker_tools import extract_bond_country

class MwBondSpider(scrapy.Spider):
    '''
    Spider for MarketWatch bond ticker data.
    name :  'mw_bonds'
    '''
    name = "mw_bonds"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/bonds"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        currencies = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for currency in currencies:
            loader = ItemLoader(item=MwBondItem(), selector=currency)
            loader.add_value('asset_class', asset_class)
            sec_name = currency.xpath('.//a/text()').get()
            if sec_name:
                loader.add_value('sec_name', sec_name)
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            loader.add_xpath('industry', './/td[3]/text()')
            # sec_link = currency.xpath('.//a/@href').get()
            country_name = extract_bond_country(sec_name)
            if country_name:
                loader.add_value('country_name', country_name)
            yield loader.load_item()

        # Go to next page
            for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].getall():
                yield response.follow(next_page, callback=self.parse)

        if response.xpath('//ul[@class="pagination"]/li[@class="active"]/a/text()').get().strip() == 'A':
            other_pages = response.xpath('//ul[@class="pagination"]/li/a/@href').getall()
            other_pages.remove('#')
            for page in other_pages:
                yield response.follow(page, callback=self.parse)