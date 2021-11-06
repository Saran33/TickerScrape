import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwRateItem


class MWRateSpider(scrapy.Spider):
    '''
    Spider for MarketWatch rate ticker data.
    name :  'mw_rates'
    '''
    name = "mw_rates"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/rates"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        rates = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for rate in rates:
            loader = ItemLoader(item=MwRateItem(), selector=rate)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            # sec_link = rate.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].getall():
                yield response.follow(next_page, callback=self.parse)