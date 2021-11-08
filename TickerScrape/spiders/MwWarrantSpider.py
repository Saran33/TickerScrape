import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwWarrantItem


class MwWarrantSpider(scrapy.Spider):
    '''
    Spider for MarketWatch warrant ticker data.
    name :  'mw_warrants'
    '''
    name = "mw_warrants"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/warrants/a-z"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        countries = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="list-unstyled"]/li/a')
        for country in countries:
            country_link = country.xpath('.//@href').get()
            request = response.follow(country_link, self.parse_country)
            if request:
                yield request

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        warrants = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for warrant in warrants:
            loader = ItemLoader(item=MwWarrantItem(), selector=warrant)
            loader.add_value('asset_class', asset_class)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('country_name', './/td[2]/text()')
            loader.add_xpath('exchange', './/td[3]/text()')
            loader.add_xpath('industry', './/td[4]/text()')
            # sec_link = warrant.xpath('.//a/@href').get()
            yield loader.load_item()

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
