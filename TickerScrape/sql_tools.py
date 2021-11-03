
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import asc, desc, func
from scrapy.exceptions import DropItem
from TickerScrape.models import Article, Tag, db_connect, create_table, Topic, Source, Author, SnipBlob, Blob, SnipVader, Vader #  create_output_table
# from FiScrape.spiders.FiSpider import query
import logging
from ln_meta import uri as uri

uri = uri
# con = 'sqlite:///DN_name.db'
# uri = 'sqlite:///DN_name.db'
# from os import environ
# uri = environ.get('CONNECTION_STRING')
# from scrapy.utils.project import get_project_settings
# uri = get_project_settings().get("CONNECTION_STRING")
# self.engine = create_engine(db_uri, echo=True)

def nlp_connect(uri):
    # engine = db_connect()
    engine = create_engine(uri)
    # create_table(engine)
    # Session = sessionmaker(bind=engine)
    # session = Session()
    connection = engine.connect()
    logging.info("****_NLP_Pipeline: database connected****")

    return connection

def get_snippet_sent(uri, pub_source='ft'):
    """Get a list of blob and VADER scores for a publication, ordered by datetime.
    pub_source  :   Publication source name. e.g. 'bloomberg', or 'ft'.
    """
    connection = nlp_connect(uri)
    # sql = '''SET NOCOUNT ON
    # CREATE TEMP TABLE temp_sent AS SELECT published_date, id FROM article WHERE article.source_id ='1';
    # CREATE TEMP TABLE temp_sent2 AS SELECT temp_sent.id, published_date, subjectivity, polarity FROM temp_sent INNER JOIN snip_blob ON snip_blob.article_id = temp_sent.id;
    # CREATE TEMP TABLE sentiment AS SELECT temp_sent2.id, published_date, subjectivity, polarity, compound, negative, neutral, positive FROM temp_sent2 INNER JOIN snip_vader ON snip_vader.article_id = temp_sent2.id;
    # SELECT * FROM sentiment;
    # '''
    sql1 = f"CREATE TEMP TABLE temp_sent AS SELECT published_date, id FROM article WHERE article.source_id = (SELECT rowid FROM Source WHERE name = '{pub_source}');"
    connection.execute(sql1)
    sql2 = "CREATE TEMP TABLE temp_sent2 AS SELECT temp_sent.id, published_date, subjectivity, polarity FROM temp_sent INNER JOIN snip_blob ON snip_blob.article_id = temp_sent.id;"
    connection.execute(sql2)
    sql3 = "CREATE TEMP TABLE sentiment AS SELECT temp_sent2.id, published_date, subjectivity, polarity, compound, negative, neutral, positive FROM temp_sent2 INNER JOIN snip_vader ON snip_vader.article_id = temp_sent2.id;"
    connection.execute(sql3)

    query_str = "SELECT * FROM sentiment;"
    # query_str = sql
    df_sent = pd.read_sql(query_str, con=connection, index_col='published_date', coerce_float=True, parse_dates='published_date')
    connection.execute("DROP TABLE temp_sent")
    connection.execute("DROP TABLE temp_sent2;")
    connection.execute("DROP TABLE sentiment;")
    return df_sent

def get_total_articles(session, ascending=True):  # source_name
    """Get the total articles stord for a publication source."""
    if not isinstance(ascending, bool):
        raise ValueError(f"Sorting value invalid: {ascending}")

    direction = asc if ascending else desc

    return (
        session.query(
            Source.name, func.count(Article.headline).label("total_articles")
        )
        .join(Source.articles)
        .group_by(Source.name)
        .order_by(direction("total_articles"))
    )
