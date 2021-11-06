import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwETFItem

class MwETFSpider(scrapy.Spider):
    '''
    Spider for MarketWatch index ticker data.
    name :  'mw_etfs'
    '''
    name = "mw_etfs"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/exchange-traded-funds/a-z"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        etfs = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for etf in etfs:
            loader = ItemLoader(item=MwETFItem(), selector=etf)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            loader.add_xpath('country_name', './/td[3]/text()')
            loader.add_xpath('industry', './/td[4]/text()')
            # sec_link = etf.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].getall():
                yield response.follow(next_page, callback=self.parse)

        if response.xpath('//ul[@class="pagination"]/li[@class="active"]/a/text()').get().strip() == 'A':
            other_pages = response.xpath('//ul[@class="pagination"]/li/a/@href').getall()
            other_pages.remove('#')
            for page in other_pages:
                yield response.follow(page, callback=self.parse)