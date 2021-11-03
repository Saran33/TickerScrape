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
    text = normalize("NFKD", ''.join(map(str, text)).replace('  ', ' ').strip())
    return text

def remove_space(text):
    # strip the unicode articles
    return text.replace('  ', ' ').strip()
    # .lstrip()
    # .rstrip()
    # For X- path, you can also use: normalize-space

def extract_headline(text):
    #text = "".join(text)
    #text = text.strip(u'\u201c'u'\u201d')
    text = text.replace('  ', ' ')
    return text

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

def remove_mail_to(text):
    return text.replace("mailto:", '').strip()

def add_ft_domain(text):
    domain_name ='https://www.ft.com'
    return f"{domain_name}{text}".strip()

def add_bi_domain(text):
    domain_name ='https://www.businessinsider.com'
    return f"{domain_name}{text}".strip()

def add_bbc_domain(text):
    domain_name ='https://www.bbc.co.uk'
    return f"{domain_name}{text}".strip()

def add_zh_domain(text):
    domain_name ='https://www.zerohedge.com'
    return f"{domain_name}{text}".strip()

def add_cnbc_domain(text):
    domain_name ='https://www.cnbc.com'
    return f"{domain_name}{text}".strip()

# def add_domain(text):
#     # Add a domain to a url extension
#     text = f"{allowed_domains+text}"

def parse_location(text):
    # parse location "in Ulm, Germany"
    # this simply remove "in ", you can further parse city, state, country, etc.
    return text[3:]

def strip_bbc_h2(text):
    return  text.replace(' class="ssrcss-1s5ma9r-StyledHeading e1fj1fc10"', '').replace('class="ssrcss-1s5ma9r-StyledHeading e1fj1fc10', '').replace(
        ' class="ssrcss-1s5ma9r-StyledHeading ', '').replace('e1fj1fc10"', '')

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

def remove_read_more(text):
    return text.replace(' read more ', '')

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

class FtArtItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_ft_dt),
        # TakeFirst return the first value not the whole list
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    # standfirst = Field(
    #     input_processor=MapCompose(extract_standfirst),
    #     output_processor=Join()
    #     )
    standfirst = Field(
        # Processed in pipeline due to limitations of Scrapy processors
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        # TakeFirst return the first value not the whole list
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(add_ft_domain),
        output_processor=TakeFirst()
        )
    # authors = Field(
    #     )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()
# # class ProfileField(scrapy.item.Field):

# class FT_AuthorItem(Item):
    # author_name = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=TakeFirst()
    #     )
    # author_position = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=Join()
    #     )
    # author_bio = Field(
    #     input_processor=MapCompose(strip_ft_bio),
    #     output_processor=Join()
    #     )
    # author_twitter = Field(
    #     input_processor=MapCompose(str.strip),
    #     output_processor=TakeFirst()
    #     )
    # author_email = Field(
    #     input_processor=MapCompose(remove_mail_to),
    #     output_processor=TakeFirst()
    #     )
    # author_birthday = Field(
    #     input_processor=MapCompose(convert_date),
    #     output_processor=TakeFirst()
    # )
    # author_bornlocation = Field(
    #     input_processor=MapCompose(parse_location),
    #     output_processor=TakeFirst()
    # )

# class AuthorItemLoader(ItemLoader):
#     default_input_processor=MapCompose(str.strip)
#     default_output_processor=TakeFirst()
#     default_item_class=FT_AuthorItem

class InsiderArtItem(Item):
    published_date = Field(
        input_processor=MapCompose(convert_bi_dt),
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    standfirst = Field(
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(add_bi_domain),
        output_processor=TakeFirst()
        )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()

class BBCArtItem(Item):
    published_date = Field(
        input_processor=MapCompose(parse_utc_dt),
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    standfirst = Field(
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(remove_articles, strip_bbc_h2),
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(str.strip), # add_bbc_domain
        output_processor=TakeFirst()
        )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()


class ZhArtItem(Item):
    published_date = Field(
        input_processor=MapCompose(parse_to_utc),
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    # standfirst = Field(
    #     )
    standfirst = Field(
        input_processor=Compose(remove_articles),
        output_processor=Identity()
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(bleach_html, remove_articles, remove_space),
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(add_zh_domain),
        output_processor=TakeFirst()
        )
    origin_link = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()

class CNBCArtItem(Item):
    published_date = Field(
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    standfirst = Field(
        input_processor=Compose(remove_articles),
        output_processor=Identity()
        )
    article_summary = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(bleach_html, remove_articles, remove_space),
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    origin_link = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    authors = Field(
        input_processor=Identity()
        )
    tags = Field()

class ReutersArtItem(Item):
    published_date = Field(
        output_processor=TakeFirst()
        )
    headline = Field(
        input_processor=MapCompose(extract_headline),
        output_processor=Join()
        )
    standfirst = Field(
        input_processor=Compose(remove_articles),
        output_processor=Identity()
        )
    article_summary = Field(
        input_processor=MapCompose(bleach_html, and_amp, extract_headline),
        output_processor=Join()
        )
    image_caption = Field(
        input_processor=MapCompose(and_amp, remove_articles),
        output_processor=Join()
        )
    article_content = Field(
        input_processor=MapCompose(bleach_html, remove_read_more, remove_p_tspace, and_amp, remove_articles, remove_space),
        output_processor=Join()
        )
    article_footnote = Field(
        input_processor=MapCompose(remove_articles),
        output_processor=Join()
        )
    article_link = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    origin_link = Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
        )
    authors = Field(input_processor=Identity()
        )
    tags = Field()