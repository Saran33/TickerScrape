import warnings
warnings.filterwarnings('ignore')
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from TickerScrape.spiders.MwADRSpider  import MwADRSpider
from TickerScrape.spiders.MwBenchmarkSpider import MwBenchmarkSpider
from TickerScrape.spiders.MwBondSpider import MwBondSpider
from TickerScrape.spiders.MwCryptoSpider import MwCryptoSpider
from TickerScrape.spiders.MwCurrencySpider import MwCurrencySpider
from TickerScrape.spiders.MwETFSpider import MwETFSpider
from TickerScrape.spiders.MwETNSpider import MwETNSpider
from TickerScrape.spiders.MwFundSpider import MwFundSpider
from TickerScrape.spiders.MwFuturesSpider import MwFuturesSpider
from TickerScrape.spiders.MwIndexSpider import MwIndexSpider
from TickerScrape.spiders.MwRateSpider import MwRateSpider
from TickerScrape.spiders.MwReitSpider import MwReitSpider
from TickerScrape.spiders.MwStockSpider import MwStockSpider
from TickerScrape.spiders.MwWarrantSpider import MwWarrantSpider

# scrapy runspider TickerScrape.py
# python3 TickerScrape.py

process = CrawlerProcess(get_project_settings())
process.crawl(MwStockSpider)
process.crawl(MwRateSpider)
process.crawl(MwFundSpider)
process.crawl(MwBondSpider)
process.crawl(MwBenchmarkSpider)
process.crawl(MwReitSpider)
process.crawl(MwFuturesSpider)
process.crawl(MwADRSpider)
process.crawl(MwETNSpider)
process.crawl(MwWarrantSpider)
process.crawl(MwIndexSpider)
process.crawl(MwETFSpider)
process.crawl(MwCurrencySpider)
process.crawl(MwCryptoSpider)
process.start()


# setting = get_project_settings()
# process = CrawlerProcess(setting)

# for spider_name in process.spiders.list():
#     print ("Running spider %s" % (spider_name))
#     process.crawl(spider_name,query="dvh") #query dvh is custom argument used in your scrapy

# process.start()


# # OR via shell script:

# scrapy runspider mw_stocks &
# scrapy runspider mw_fx &
# scrapy runspider mw_bonds &
# scrapy runspider mw_etfs

# chmod +x TickerScrape.py

# # To schedule a cronjob every 6 hours:
# crontab -e
# * */6 * * * path/to/shell/TickerScrape.py >> path/to/file.log