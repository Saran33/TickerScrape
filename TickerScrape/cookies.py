from http.cookies import SimpleCookie
from urllib.parse import urlparse, parse_qs, urlencode
import json

# CNBC
CNBC_URL = f'https://api.queryly.com/cnbc/json.aspx?queryly_key=31a35d40a9a64ab3&query={query}&endindex=0&batchsize=10&callback=&showfaceted=false&timezoneoffset=-240&facetedfields=formats&facetedkey=formats%7C&facetedvalue=!Press%20Release%7C&sort=date&additionalindexes=4cd6f71fbf22424d,937d600b0d0d4e23,3bfbe40caee7443e,626fdfcd96444f28'


def parse_new_cnbc_url(url, page_number):
    url_parsed = urlparse(url)
    query_string = parse_qs(url_parsed.query)
    batchsize = json.loads(query_string.get('batchsize')[0])
    if page_number == 1:
        endindex = 0
    else:
        endindex = (page_number*batchsize)-batchsize
    new_url = f'https://api.queryly.com/cnbc/json.aspx?queryly_key=31a35d40a9a64ab3&query={query}&endindex={endindex}&batchsize=10&callback=&showfaceted=false&timezoneoffset=-240&facetedfields=formats&facetedkey=formats%7C&facetedvalue=!Press%20Release%7C&sort=date&additionalindexes=4cd6f71fbf22424d,937d600b0d0d4e23,3bfbe40caee7443e,626fdfcd96444f28'
    return new_url

# parse_new_cnbc_url(CNBC_URL, 4)



# Bloomberg
bloom_url = f'https://www.bloomberg.com/markets2/api/search?query={query}&page=1&sort=time:desc'

def parse_new_bloom_url(page_number):
    return f'https://www.bloomberg.com/markets2/api/search?query={query}&page={page_number}&sort=time:desc'



# Reuters
reuters_api = f'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?query=%7B%22keyword%22%3A%22Bitcoin%22%2C%22offset%22%3A0%2C%22orderby%22%3A%22display_date%3Adesc%22%2C%22size%22%3A10%2C%22website%22%3A%22reuters%22%7D&d=53&_website=reuters'


def parse_new_reut_url(url, page_number):
    # print (url)
    # print ('')
    url_parsed = urlparse(url)
    # print(url_parsed.query)
    query_string = parse_qs(url_parsed.query)
    # print ("query_string:", query_string)
    # print(type(query_string))
    search_query_state = json.loads(query_string.get('query')[0])
    # print(search_query_state)
    offset = search_query_state.get('offset')
    size = search_query_state.get('size')
    # print (offset)
    if page_number == 1:
        offset = 0
    else:
        offset = (page_number*size)-size
    # print (offset)
    search_query_state['offset'] = offset
    search_query_str = str(search_query_state).replace(' ', '').replace(
        "'", '"').replace('["', "['").replace('"]', "']")
    query_string.get('query')[0] = search_query_str
    # print ('')
    # print("New query_string:", query_string)
    encoded_qs = urlencode(query_string, doseq=1)
    new_url = f'https://www.reuters.com/pf/api/v3/content/fetch/articles-by-search-v2?{encoded_qs}'
    # print ('')
    # print (new_url)
    return new_url


# parse_new_reut_url(reuters_api, 3)


def cookie_parser():
    cookie_string = 'zguid=23|%24066a0ab1-2789-4161-a124-20bc5cdf6baa; zgsession=1|b47e84ca-ddce-4b93-9aa9-d7bce9222355; _ga=GA1.2.2101909177.1633620553; _gid=GA1.2.1915240197.1633620553; zjs_user_id=null; zjs_anonymous_id=%22066a0ab1-2789-4161-a124-20bc5cdf6baa%22; _pxvid=5354ff01-2783-11ec-97dd-484d664d654d; _gcl_au=1.1.1487869565.1633620553; KruxPixel=true; DoubleClickSession=true; __pdst=50aa09dfbf134fcc84b09fc3aff95e8e; _fbp=fb.1.1633620554004.923846820; _pin_unauth=dWlkPU5tRXpNamhpWmpVdE9XUm1OUzAwTXpneUxXRmtOR0V0WkRkalpETmtNekl6T1RGaA; utag_main=v_id:017c5b5f6f45001c995e3a5fccf005078001707000bd0$_sn:1$_se:1$_ss:1$_st:1633622353542$ses_id:1633620553542%3Bexp-session$_pn:1%3Bexp-session$dcsyncran:1%3Bexp-session$tdsyncran:1%3Bexp-session$dc_visit:1$dc_event:1%3Bexp-session$dc_region:eu-central-1%3Bexp-session$ttd_uuid:64a909d4-8912-45a5-95c3-d5e4c968c625%3Bexp-session; KruxAddition=true; JSESSIONID=7E361F7E94784D1729FBC01B57FF66D7; __gads=ID=02eb728a5547dc81:T=1633620567:S=ALNI_MZBKoXXS_k5lySxQtTibkjn55L0Cg; _uetsid=53641650278311ecb8c5dbd5361edc46; _uetvid=536457e0278311ec88ef594a0f80b8d2; _px3=a0e1da38392f5014012d0b8c7dfc7b67dfcb6e15cbec1aa1c8b811775a75c568:TEfgCB1KnHuoWxvY9OoSZDRtcoCTq1Kk//ZxMyuYBMy/CviV1WigGuzOpaHWatMUDl1/ToyB1EUPk4+Nn3oSyA==:1000:NyHYQx7CEUw45JseFtcWSr7NtivXEznSTFDk193qEn0RmR1jFz7DNYrxAoAfYgy6bZouHMNIzebLokFG8oy5AvSLF/CXNemSFj/MybQ1Oom6dUEDxzWWpPaceEYrUifUi30OWZ4idj/LeR2M8NTeaDAw2UgMKWAOASvftK28o1EcvXobpq40K8AdBoXc4BStxi+YkYWKSPN8Xz4f2TGrcw==; AWSALB=pcb+lLJgHdvkrLPcsdGbDndPmBrLxalAZRXleSJ4eWNMRUUN8A7DPM+GMiuddeU7EFm7GjWl0WLvlbifXWOllKj0aPEo0UkqVEeUIn0LE7kCn7xbhHSfC98l/nq8; AWSALBCORS=pcb+lLJgHdvkrLPcsdGbDndPmBrLxalAZRXleSJ4eWNMRUUN8A7DPM+GMiuddeU7EFm7GjWl0WLvlbifXWOllKj0aPEo0UkqVEeUIn0LE7kCn7xbhHSfC98l/nq8; search=6|1636213533046%7Crect%3D25.855607%252C-80.142305%252C25.596685%252C-80.456276%26rid%3D12700%26disp%3Dmap%26mdm%3Dauto%26p%3D2%26z%3D1%26fs%3D1%26fr%3D0%26mmm%3D0%26rs%3D0%26ah%3D0%26singlestory%3D0%26housing-connector%3D0%26abo%3D0%26garage%3D0%26pool%3D0%26ac%3D0%26waterfront%3D0%26finished%3D0%26unfinished%3D0%26cityview%3D0%26mountainview%3D0%26parkview%3D0%26waterview%3D0%26hoadata%3D1%26zillow-owned%3D0%263dhome%3D0%26featuredMultiFamilyBuilding%3D0%26excludeNullAvailabilityDates%3D0%09%0912700%09%09%09%09%09%09; _gat=1'
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    # print (cookie.items())

    cookies = {}

    for key, morsel in cookie.items():
        cookies[key] = morsel.value

    # print(cookies)
    return cookies

# cookie_parser()
