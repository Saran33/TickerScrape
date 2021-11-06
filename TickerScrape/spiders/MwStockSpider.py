import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import MwStockItem
import requests as rq
from bs4 import BeautifulSoup
from lxml import etree
from TickerScrape.items import to_float, curr_str_to_float, perc_str_to_float, to_int


class MWStocksSpider(scrapy.Spider):
    '''
    Spider for MarketWatch stock ticker data.
    name :  'mw_stocks'
    '''
    name = "mw_stocks"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = ["https://www.marketwatch.com/tools/markets/stocks"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        countries = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="list-unstyled"]/li/a')
        for country in countries:
            country_link = country.xpath('.//@href').get()
            request = response.follow(country_link, self.parse_country)
            if request:
                yield request

    def parse_country(self, response):
        asset_class = response.xpath(
            '//*[@id="marketsindex"]/ul[@class="nav nav-pills"]/li[@class="active"]/a/text()').get()
        country_name = response.xpath(
            '//*[@id="marketsindex"]/h2/text()').get()
        country_name = country_name.replace('Location: ', '')
        stocks = response.xpath('//*[@id="marketsindex"]/table/tbody/tr')
        for stock in stocks:
            loader = ItemLoader(item=MwStockItem(), selector=stock)
            loader.add_value('asset_class', asset_class)
            loader.add_value('country_name', country_name)
            loader.add_xpath('sec_name', './/a/text()')
            loader.add_xpath('ticker', './/a/small/text()')
            loader.add_xpath('exchange', './/td[2]/text()')
            loader.add_xpath('industry', './/td[3]/text()')
            sec_link = stock.xpath('.//a/@href').get()
            security_item = loader.load_item()
            request = response.follow(sec_link, self.parse_security, meta={
                                      'security_item': security_item})
            request.meta['security_item'] = security_item
            if request:
                yield request
            else:
                yield security_item

        # # Go to next page
        # # if response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li[@class="active"]/span/text()').get() == '1':
        # #     for a in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[:-1].getall():
        # #         yield response.follow(a, callback=self.parse)
        # for next_page in response.xpath('//*[@id="marketsindex"]/ul[@class="pagination"]/li/a/@href')[-1].get():
        #     yield response.follow(next_page, callback=self.parse)

    def parse_security(self, response):
        security_item = response.meta['security_item']
        loader = ItemLoader(item=security_item, response=response)
        profile_url = response.xpath(
            '//a[@instrument-target="company-profile"]/@href').get()
        if profile_url:
            self.parse_profile(security_item, profile_url)
        analyst_url = response.xpath(
            '//a[@instrument-target="analystestimates"]/@href').get()
        if analyst_url:
            self.parse_analyst(security_item, analyst_url)

        sec_beta = response.xpath(
            '//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[7]/span[1]/text()').get()
        if sec_beta:
            loader.add_value('sec_beta', sec_beta)
        market_cap = response.xpath(
            '//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[4]/span[1]/text()').get()
        if market_cap:
            loader.add_value('market_cap', market_cap)
        pe_ratio = response.xpath(
            '//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[9]/span[1]/text()').get()
        if pe_ratio:
            loader.add_value('pe_ratio', pe_ratio)
        short_int = response.xpath(
            '//*[@id="maincontent"]/div[6]/div[1]/div[1]/div/ul/li[14]/span[1]/text()').get()
        if short_int:
            # print("SHORT_INT:", short_int)
            loader.add_value('short_int', short_int)

        yield loader.load_item()

    def parse_profile(self, security_item, profile_url):
        response = rq.get(url=profile_url)
        page_source = BeautifulSoup(response.text, 'lxml')
        dom = etree.HTML(str(page_source))
        try:
            price_to_sales = [to_float(text.strip()) for text in dom.xpath(
                './/table[@aria-label="VALUATION data table"]/tbody/tr[4]/td[2]/text()')][0]
            security_item['price_to_sales'] = price_to_sales
        except:
            pass
        try:
            price_to_book = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="VALUATION data table"]/tbody/tr[5]/td[2]/text()')][0]
            security_item['price_to_book'] = price_to_book
        except:
            pass
        try:
            price_to_fcf = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="VALUATION data table"]/tbody/tr[6]/td[2]/text()')][0]
            security_item['price_to_fcf'] = price_to_fcf
        except:
            pass
        try:
            net_margin = [perc_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="PROFITABILITY data table"]/tbody/tr[4]/td[2]/text()')][0]
            security_item['net_margin'] = net_margin
        except:
            pass
        try:
            roc = [perc_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="PROFITABILITY data table"]/tbody/tr[7]/td[2]/text()')][0]
            security_item['roc'] = roc
        except:
            pass
        try:
            roi = [perc_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="PROFITABILITY data table"]/tbody/tr[8]/td[2]/text()')][0]
            security_item['roi'] = roi
        except:
            pass
        try:
            debt_to_eq = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[1]/td[2]/text()')][0]
            security_item['debt_to_eq'] = debt_to_eq
        except:
            pass
        try:
            debt_to_ass = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[3]/td[2]/text()')][0]
            security_item['debt_to_ass'] = debt_to_ass
        except:
            pass
        try:
            current_ratio = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="LIQUIDITY data table"]/tbody/tr[1]/td[2]/text()')][0]
            security_item['current_ratio'] = current_ratio
        except:
            pass
        try:
            quick_ratio = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="LIQUIDITY data table"]/tbody/tr[2]/td[2]/text()')][0]
            security_item['quick_ratio'] = quick_ratio
        except:
            pass
        try:
            cash_ratio = [to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="LIQUIDITY data table"]/tbody/tr[3]/td[2]/text()')][0]
            security_item['cash_ratio'] = cash_ratio
        except:
            pass
        try:
            sec_summary = [text.strip() for text in dom.xpath(
                '//p[@class="description__text"]/text()')][0]
            security_item['sec_summary'] = sec_summary
        except:
            pass
        return security_item

    def parse_analyst(self, security_item, analyst_url):
        response = rq.get(url=analyst_url)
        page_source = BeautifulSoup(response.text, 'lxml')
        dom = etree.HTML(str(page_source))
        try:
            average_rec = [text.strip() for text in dom.xpath(
                './/table[@aria-label="snapshot data table"]/tbody/tr[1]/td[2]/text()')][0]
            security_item['average_rec'] = average_rec
        except:
            pass
        try:
            no_of_ratings = [to_int(text.strip()) for text in dom.xpath(
                '//table[@aria-label="snapshot data table"]/tbody/tr[3]/td[2]/text()')][0]
            security_item['no_of_ratings'] = no_of_ratings
        except:
            pass
        try:
            high_target = [curr_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="stock price targets data table"]/tbody/tr[1]/td[2]/text()')][0]
            security_item['high_target'] = high_target
        except:
            pass
        try:
            median_target = [curr_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="stock price targets data table"]/tbody/tr[2]/td[2]/text()')][0]
            security_item['median_target'] = median_target
        except:
            pass
        try:
            low_target = [curr_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="stock price targets data table"]/tbody/tr[3]/td[2]/text()')][0]
            security_item['low_target'] = low_target
        except:
            pass
        try:
            avg_target = [curr_str_to_float(text.strip()) for text in dom.xpath(
                '//table[@aria-label="stock price targets data table"]/tbody/tr[4]/td[2]/text()')][0]
            security_item['avg_target'] = avg_target
        except:
            pass
        return security_item

    # def parse_profile(self, response):
    #     security_item = response.meta['security_item']
    #     loader = ItemLoader(item=security_item, response=response)
    #     price_to_sales = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[4]/td[2]/text()').get()
    #     if price_to_sales:
    #         loader.add_value('price_to_sales', price_to_sales)
    #     price_to_book = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[5]/td[2]/text()').get()
    #     if price_to_book:
    #         loader.add_value('price_to_book', price_to_book)
    #     price_to_fcf = response.xpath('//table[@aria-label="VALUATION data table"]/tbody/tr[6]/td[2]/text()').get()
    #     if price_to_fcf:
    #         loader.add_value('price_to_fcf', price_to_fcf)
    #     net_margin = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[4]/td[2]/text()').get()
    #     if net_margin:
    #         loader.add_value('net_margin', net_margin)
    #     roc = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[7]/td[2]/text()').get()
    #     if roc:
    #         loader.add_value('roc', roc)
    #     roi = response.xpath('//table[@aria-label="PROFITABILITY data table"]/tbody/tr[8]/td[2]/text()').get()
    #     if roi:
    #         loader.add_value('roi', roi)
    #     debt_to_eq = response.xpath('//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[1]/td[2]/text()').get()
    #     if debt_to_eq:
    #         loader.add_value('debt_to_eq', debt_to_eq)
    #     debt_to_ass = response.xpath('//table[@aria-label="CAPITALIZATION data table"]/tbody/tr[3]/td[2]/text()').get()
    #     if debt_to_ass:
    #         loader.add_value('debt_to_ass', debt_to_ass)
    #     current_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[1]/td[2]/text()').get()
    #     if current_ratio:
    #         loader.add_value('current_ratio', current_ratio)
    #     quick_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[2]/td[2]/text()').get()
    #     if quick_ratio:
    #         loader.add_value('quick_ratio', quick_ratio)
    #     cash_ratio = response.xpath('//table[@aria-label="LIQUIDITY data table"]/tbody/tr[3]/td[2]/text()').get()
    #     if cash_ratio:
    #         loader.add_value('cash_ratio', cash_ratio)
    #     sec_summary = response.xpath('//p[@class="description__text"]/text()').get()
    #     if sec_summary:
    #         loader.add_value('sec_summary', sec_summary)
    #     yield loader.load_item()
