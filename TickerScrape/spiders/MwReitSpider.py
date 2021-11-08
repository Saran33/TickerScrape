import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwReitItem


class MwReitSpider(scrapy.Spider):
    '''
    Spider for MarketWatch reit ticker data.
    name :  'mw_reits'
    '''
    name = "mw_reits"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/real-estate-investment-trusts/a-z",
                  "https://www.marketwatch.com/tools/markets/real-estate-investment-trusts/a-z/0-9"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        currencies = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for currency in currencies:
            loader = ItemLoader(item=MwReitItem(), selector=currency)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            loader.add_xpath('industry', './/td[3]/text()')
            # sec_link = currency.xpath('.//a/@href').get()
            yield loader.load_item()

        # Go to next page
            for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].getall():
                yield response.follow(next_page, callback=self.parse)

        active_page = response.xpath(
            '//ul[@class="pagination"]/li[@class="active"]/a/text()').get()
        if active_page:
            if active_page.strip() == 'A':
                other_pages = response.xpath(
                    '//ul[@class="pagination"]/li/a/@href').getall()
                if other_pages:
                    other_pages.remove('#')
                    for page in other_pages:
                        yield response.follow(page, callback=self.parse)
