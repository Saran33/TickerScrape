import scrapy
from scrapy.loader import ItemLoader
from TickerScrape.items import FtArtItem, convert_ft_dt
from unicodedata import normalize
from bs4 import BeautifulSoup
import grequests


class MWStocksSpider(scrapy.Spider):
    '''
    Spider for MarketWatch stock ticker data.
    name :  'mw'
    '''
    name = "mw"

    # allowed_domains = ['marketwatch.com']
    # domain_name ='https://www.marketwatch.com'
    start_urls = [f"https://www.marketwatch.com/tools/markets/stocks"]

    def parse(self, response):
        self.logger.info('Parse function called on {}'.format(response.url))
        article_snippets = response.css('div.o-teaser.o-teaser--article.o-teaser--small.o-teaser--has-image.js-teaser')

        for snippet in article_snippets:
            published_date = snippet.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)').get()
            published_date = convert_ft_dt(published_date)
            if published_date >= start_date:
                loader = ItemLoader(item=FtArtItem(), selector=snippet)
                loader.add_css('published_date',
                               'div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')
                loader.add_css('headline', "a.js-teaser-heading-link *::text")
                loader.add_css('standfirst', "p.o-teaser__standfirst *::text")
                loader.add_css('tags', "a.o-teaser__tag::text")
                loader.add_css('article_link', "div.o-teaser__heading a::attr(href)")
                article_url = snippet.css('div.o-teaser__heading a::attr(href)').get()
                # go to the article page and pass the current collected article info
                # self.logger.info('Get article page url')
                article_item = loader.load_item()
                request = response.follow(article_url, self.parse_article, meta={'article_item': article_item})
                request.meta['article_item'] = article_item
                if request:
                    yield request
                else:
                    yield article_item

        last_date = response.css('div.o-teaser__timestamp time.o-teaser__timestamp-date::attr(datetime)')[-1].extract()
        last_date = convert_ft_dt(last_date)
        if last_date >= start_date:
            # Go to next search page
            for a in response.xpath(
                    ".//a[@class='search-pagination__next-page o-buttons o-buttons--secondary o-buttons-icon o-buttons-icon--arrow-right o-buttons--big o-buttons-icon--icon-only']"):
                yield response.follow(a, callback=self.parse)

    def parse_article(self, response):
        article_item = response.meta['article_item']
        loader = ItemLoader(item=article_item, response=response)
        article_item['authors'] = {}
        authors = response.css("a.n-content-tag--author")
        bio_links = []
        if authors:
            for author in authors:
                auth = author.css("a.n-content-tag--author::text").get()
                article_item['authors'][f'{auth}'] = {}
                bio_link = author.css("a.n-content-tag--author::attr(href)").extract()
                bio_link = response.urljoin(''.join(map(str, bio_link)))
                article_item['authors'][f'{auth}']['bio_link'] = bio_link
                bio_links.append(bio_link)
            resp = self.get_urls(bio_links)
            self.process_author(article_item, resp)

        article_summary = response.xpath('.//*[@class="o-topper__standfirst"]/text()').get()
        if article_summary:
            loader.add_value('article_summary', article_summary)
        image_caption = response.xpath('//*[@id="site-content"]/div[1]/figure/figcaption/text()').getall()
        if image_caption:
            loader.add_value('image_caption', image_caption)
        article_content = response.xpath(
            '//*[contains(@class, "article__content-body n-content-body js-article__content-body")]//text()[not(ancestor::*[@class="n-content-layout__container"])]').getall()
        if article_content:
            loader.add_value('article_content', article_content)
        article_footnote = response.xpath('//*[contains(@class, "article__content-body n-content-body js-article__content-body")]/p[1]/*[self::em or self::a]//text()[not(ancestor::*[@class="n-content-layout__container"])]').getall()
        if article_footnote:
            loader.add_value('article_footnote', article_footnote)
        article_footnote_2 = response.xpath('.//*[@id="site-content"]/div[3]/div[2]/p[last()-1]/em/text()').get()
        if article_footnote_2:
            loader.add_value('article_footnote', article_footnote_2)
        yield loader.load_item()


    def get_urls(self, bio_links):
        reqs = [grequests.get(bio_link) for bio_link in bio_links]
        resps = grequests.map(reqs)
        return resps


    def process_author(self, article_item, resps):
        authors = article_item['authors']
        for (auth, response) in zip(authors.keys(), resps):
            page_source = BeautifulSoup(response.text, 'lxml')
            try:
                pos = page_source.find('div', attrs={'class': "sub-header__strapline"}).text.strip()
                article_item['authors'][f'{auth}']['author_position'] = pos
            except:
                pass
            try:
                author_bio = page_source.find('div', attrs={'class': "sub-header__description"}).text
                author_bio = normalize("NFKD", ''.join(map(str, author_bio)).replace('  ', ' ').strip())
                article_item['authors'][f'{auth}']['author_bio'] = author_bio
            except Exception as e:
                print(f'error getting bio. #{e}')
            try:
                article_item['authors'][f'{auth}']['author_email'] = page_source.find('a', attrs={
                    'data-trackable': 'send-email'})['href'].replace('mailto:', '').strip()
            except:
                pass
            try:
                article_item['authors'][f'{auth}']['author_twitter'] = page_source.find('a', attrs={
                    'data-trackable': 'twitter-page'})['href'].strip()
            except:
                pass
        return article_item