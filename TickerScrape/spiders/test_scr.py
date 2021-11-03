
import scrapy
import pandas as pd
import re
import os
from FiScrape.items import TestItem
# Download the full page HTML to see how it renders for scrapy (check for JS)
# To run, use:
# scrapy crawl test
# scrapy crawl test --nolog

class TestSpider(scrapy.Spider):
    name = "test"

    def start_requests(self):
        """Loop through a CSV of links and return the html for each page."""

        default_file = "csv_files/news_sites/btc_news_sites.csv"
        test_file = "csv_files/news_sites/btc_news_sites_test.csv"

        f_path = input('Enter a csv file path with a "URL" columm (d for default, t for test): ').strip().strip('"').strip("'")
        if f_path.lower() == 'd':
            f_path = default_file
        elif f_path.lower() == 't':
            f_path = test_file
        if os.path.exists(f_path) == True:
            print ("Loading CSV...")
            print (f_path)
    
        elif os.path.exists(f_path) == False:
            print (f"No file exists called: '{f_path}'")
            return

        df = pd.read_csv(f_path)
        self.start_url = []
        if "url" in df.columns:
            df["URL"] = df["url"]
        [self.start_url.append(url) for url in df["URL"]]

        out_dir = 'html_files'
        check_path = os.path.isdir(out_dir)
        if not check_path:
            os.makedirs(out_dir)

        for url in self.start_url:
            self.a = 0
            self.url = url
            self.page = self.url.split("/")[-1]
            try:
                site = re.search(r'\.(.*?)\.', url).group(1)
            except:
                site = re.search(r'\//(.*?)\.', url).group(1)
            site = site.replace('-', '_')
            self.filename = f'html_files/{site}.html'

            # with open(self.filename, 'wb') as f:
            #     f.write('URL:;'+self.url+'\n')
            request = scrapy.Request(url=self.url,callback=self.parse,dont_filter = True)
            request.meta['url'] = url
            yield request

    def parse(self, response):
        self.file = response.meta['url']
        try:
            site = re.search(r'\.(.*?)\.', self.file).group(1)
        except:
            site = re.search(r'\//(.*?)\.', self.file).group(1)
        site = site.replace('-', '_')
        filename = f'html_files/{site.split("/")[-1]}.html'
        body = TestItem()
        with open(filename, 'wb') as f:
            f.write(response.body)
        print ("SAVED HTML to:", filename)