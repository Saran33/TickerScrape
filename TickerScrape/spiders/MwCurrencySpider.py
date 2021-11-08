import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwCurrencyItem


class MwCurrencySpider(scrapy.Spider):
    '''
    Spider for MarketWatch currency ticker data.
    name :  'mw_fx'
    '''
    name = "mw_fx"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/currencies"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get() 
        currencies = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for currency in currencies:
            loader = ItemLoader(item=MwCurrencyItem(), selector=currency)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            # loader.add_xpath('country_name', './/td[3]/text()')
            loader.add_xpath('industry', './/td[4]/text()')
            # sec_link = currency.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            pages = response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href').getall()
            if pages:
                next_page = None
                try:
                    next_page = pages[-1]
                except:
                    pass
                if next_page:
                    yield response.follow(next_page, callback=self.parse)
