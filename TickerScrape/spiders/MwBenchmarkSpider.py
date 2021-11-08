import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwBenchItem
from TickerScrape.ticker_tools import extract_bond_country


class MwBenchmarkSpider(scrapy.Spider):
    '''
    Spider for MarketWatch benchmark ticker data.
    name :  'mw_benchmarks'
    '''
    name = "mw_benchmarks"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/benchmarks"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        currencies = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for currency in currencies:
            loader = ItemLoader(item=MwBenchItem(), selector=currency)
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
            loader.add_value('country_name', 'country_name')
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
