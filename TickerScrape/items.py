# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

#import scrapy

from scrapy.item import Item, Field
#from scrapy.loader.processors import MapCompose, TakeFirst
from itemloaders.processors import MapCompose, TakeFirst, Compose, Join, Identity
from itemloaders import ItemLoader
from datetime import datetime,timedelta
from pytz import timezone
from tzlocal import get_localzone
from dateutil import parser
from unicodedata import normalize
import re
import bleach
from numerizer import numerize as rev_numerize
from numerize.numerize import numerize

def strip_stock_country(text):
    return text.replace('Location: ', '')

def to_float(float_str):
    try:
        fl = float(float_str)
    except:
        fl = float("NaN")
    return fl

def curr_str_to_float(cur_str, symbol='$'):
    '''Convert a currency string-formatted number into a float.'''

    num_strs = ['thousand', 'million', 'billion', 'trillion']
    for x in num_strs:
        if x in cur_str.lower():
            str_num_1 = cur_str.lower().replace(x, '').replace(',','').replace(symbol,'')
            # str_num_1 = [cur_str.replace(x, '') for x in num_strs if x in cur_str.lower()]
            if str_num_1 == cur_str:
                str_num_1 = cur_str.replace('M', '').replace('B', '').replace('T', '').replace(',','').replace(symbol,'')
            if 'm' in cur_str.lower():
                fl_num = float(str_num_1) * 1000000
            elif 'b' in cur_str.lower():
                fl_num = float(str_num_1) * 1000000000
            elif 'thousand' in cur_str.lower():
                fl_num = float(str_num_1) * 1000
            elif ('T' in cur_str) or ('trillion' in cur_str.lower()):
                fl_num = float(str_num_1) * 1000000000000
            # print ("${0:,.2f}".format(fl_num))
        else:
            fl_num = float("NaN")
    return fl_num

def float_to_curr_str(cur_float, symbol='$', decimals=0):
    '''Convert a float into a human readable shorthand format, using the numerize module.
        Then format the number with a currency symbol.'''
    cur_str = symbol + numerize(cur_float, decimals)
    return cur_str

def perc_str_to_float(perc_str):
    '''Convert a percentage string-formatted number into a float.'''
    fl_num = float(perc_str.lower().replace(',','').replace('%',''))
    return fl_num / 100

def strp_brackets(text):
    """
    Strip brackets surrounding a string.
    """
    return text.strip().strip('(').strip(')')

def strp_dt(text):
    """
    convert string '1932-03-17' to Python date, add utc timezone.
    """
    try:
        dt = datetime.strptime(text, "%Y-%m-%d")
    except:
        dt = parser.parse(text)
    # dt = timezone.utc.localize(dt)
    dt = timezone("UTC").localize(dt)
    return dt

def parse_dt(text):
    """
    convert a string to Python date with dateutil, add utc timezone if not already set.
    """
    dt = parser.parse(text)
    try:
        dt = timezone("UTC").localize(dt)
    except:
        pass
    return dt

def parse_utc_dt(text):
    """
    convert a string which already has UTC tz info to Python datetime, with dateutil.
    """
    return parser.parse(text)

def parse_to_utc(text):
    return timezone("UTC").localize(parser.parse(text))

def time_ago_str(text):
    """Converts a timedelta text string of 'n*T ago' in a UTC datetime.
    e.g. "5 days ago" will become a UTC datetime (timezone aware).
    """
    try:
        dt = parser.parse(text)
    except:
        try:
            delta = int(text.split(" ")[0])
            unit = text.split(" ")[1]
            if (unit == 'days') or (unit == 'day'):
                dt = datetime.utcnow() - timedelta(days=delta)
            elif (unit == 'hours') or (unit == 'hour'):
                dt = datetime.utcnow() - timedelta(hours=delta)
            elif (unit == 'minutes') or (unit == 'minute'):
                dt = datetime.utcnow() - timedelta(minutes=delta)
            elif (unit == 'seconds') or (unit == 'second'):
                dt = datetime.utcnow() - timedelta(seconds=delta)
            elif (unit == 'weeks') or (unit == 'week'):
                dt = datetime.utcnow() - timedelta(weeks=delta)
            elif (unit == 'microseconds') or (unit == 'microsecond'):
                dt = datetime.utcnow() - timedelta(microseconds=delta)
            dt = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        except:
            return None
    dt = timezone("UTC").localize(dt)
    return dt

def parse_to_os_tz(text):
    tz = get_localzone()
    dt = parser.parse(text)
    dt = timezone(tz.key).localize(dt)
    return dt

def join_str_lst(text):
    return ','.join(text)

def remove_articles(text):
    # strip the unicode articles
    #text = normalize("NFKD", text.strip(u'\u201c'u'\u201d'))
    text = normalize("NFKD", ''.join(map(str, text)).replace('  ', ' '))
    return text

def remove_space(text):
    # strip the unicode articles
    return text.replace('  ', ' ')
    # .lstrip()
    # .rstrip()
    # For X- path, you can also use: normalize-space

def extract_standfirst(text):
    #text =  "".join(text)
    text = text.replace('\n\t\t\t\t\t\t\n\t\t\t\t\t\t', ' ').replace('”...', '...').replace('.', '. ').replace(',', ', ').replace('  ', ' ').replace('   ', ' ')
    #text = text.strip(u'\u201c'u'\u201d')
    return text

def add_dots(text):
    return text + '...'

def clean_text(text):
    text = text.strip().replace("  ", " ").replace('  ', ' ').replace('  ', ' ')
    text = ' '.join(text.split())
    text = text.replace(' .', '. ').replace(' ,', ',')
    text = (text + '...').replace(' ...', '...').replace('......', '...')
    text = text.replace('?...', '?').replace('!...', '!').replace('-...', '-')
    text = text.replace('. .', '.').strip()
    text = text.replace(':', ': ').replace(':  ', ': ').replace(' ;', ';')
    text = text.replace('...', '... ').replace(' .', '... ').strip()
    text = text.replace('“ ', '"').replace(' ”','"').replace(" ’", "'").replace(" ’", "'")
    text = text.strip().replace("  ", " ").replace('  ', ' ').replace('  ', ' ')
    text = text.replace(' ... ..', '...').replace('......', '...').replace('..... ..', '...')
    text = text.replace('......', '...').replace('....', '...')
    text = text.replace("‘", "'").replace("’", "'").replace('“', '"').replace('”', '"')
    text = text.replace('  ', ' ')
    return text

def convert_date(text):
    """
    convert string 'March 17, 1932' to Python date
    """
    try:
        dt = datetime.strptime(text, '%B %d, %Y')
    except:
        dt = parser.parse(text)
    return dt

def convert_bi_dt(text):
    """
    convert string 'Sun Sep 26 2021 16:10:49 GMT+0000 (Coordinated Universal Time)' to Python date
    """
    text = text.replace('(Coordinated Universal Time)', '').strip()
    try:
        dt = datetime.strptime(text,"%a %b %d %Y %H:%M:%S GMT%z")
    except:
        dt = parser.parse(text)
    return dt

def convert_ft_dt(text):
    """
    convert string '1932-03-17T04:00:00+0000' to Python date
    """
    try:
        dt = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S%z")
    except:
        dt = parser.parse(text)
    return dt

def strip_ft_bio(text):
    return text.replace("\n\t\t\t\t\t\t\t\t", '').replace("\n\t\t\t\t\t\t\t", '').strip()

def index_of_nth(longstring, substring, n):
   return len(substring.join(longstring.split(substring)[: n]))

# def add_domain(text):
#     # Add a domain to a url extension
#     text = f"{allowed_domains+text}"

def strp_class(text):
    """Strips the class attribute from HTML tags."""
    cl_at = re.search(r"[a-zA-Z0-9:;\.\s\(\)\-\,]*", text).group(1)
    return text.replace(cl_at, '')

def bleach_html(text):
    tags = ['p', 'li', 'strong', 'b', 'em', 'u', 'i', 'mark', 's', 'sub', 'br', 'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'small']
    attrs = [None]
    text = bleach.clean(text, tags=tags, attributes=attrs, strip=True)
    text = text.replace('<p></p>', '').replace('<p> </p>', '').replace('<p> </p>', '').replace('<strong></strong>', '').replace('<em></em>', '')
    return [text]

def remove_p_tspace(text):
    return text.replace(' </p>', '</p>')

def and_amp(text):
    return text.replace('&amp;', '&')

# Article Items:

class TestItem(Item):
    Field(
        input_processor=Identity(),
        output_processor=Identity()
        )

class MwSecurityItem(Item):
    sec_name = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    ticker = Field(
        input_processor=MapCompose(strp_brackets),
        output_processor=TakeFirst()
        )
    exchange = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    asset_class = Field(
        output_processor=TakeFirst()
        )
    country_name = Field(
        output_processor=TakeFirst()
        )
    industry = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    sec_beta = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    market_cap = Field(
        input_processor=MapCompose(curr_str_to_float),
        output_processor=TakeFirst()
        )
    pe_ratio = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    short_int = Field(
        input_processor=MapCompose(curr_str_to_float),
        output_processor=TakeFirst()
        )
    price_to_sales = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    price_to_book = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    price_to_fcf = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    net_margin = Field(
        input_processor=MapCompose(perc_str_to_float),
        output_processor=TakeFirst()
        )
    roc = Field(
        input_processor=MapCompose(perc_str_to_float),
        output_processor=TakeFirst()
        )
    roi = Field(
        input_processor=MapCompose(perc_str_to_float),
        output_processor=TakeFirst()
        )
    debt_to_eq = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    debt_to_ass = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    current_ratio = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    quick_ratio = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    cash_ratio = Field(
        input_processor=MapCompose(to_float),
        output_processor=TakeFirst()
        )
    sec_summary = Field(
        input_processor=MapCompose(remove_space, str.strip),
        output_processor=TakeFirst()
        )
    tags = Field()