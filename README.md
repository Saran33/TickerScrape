# FiScrape
![alt text](https://github.com/PWE-Capital/FiScrape/blob/Branch36/images/PWE_FiScrape_splash.png?raw=true)
### Financial news scraping and processing for machine learning. 
`FiScrape` is a package for scraping financial news and applying natural langage processing for sentiment analysis. It leverages `scrapy`.

A search term can be queried across numerous online news sources. The resulting scraped headlines and standfirsts (and optionally the full text), along with metadata, will be timestamped and stored for each publication, along with the author and other relevent data.

Each news source on a particular topic can be stored as a seperate feature for timeseries analysis. e.g. For Bitcoin, all FT articles with "Bitcoin" in the title and/or text can comprise one set of sentiment feature. WSJ articles could be another set feature. This facilitates sentiment analysis on each publication individually, to see which, if any, yield the highest Information Coefficient or other measures of predictive merit.

Additionally, features may be further segmented by author.

Generated features can be stored locally as CSV or in a database using SQLAlchemy. The scraper can be set to run periodically.

The repository can be found at:
[Github-FiScrape](https://github.com/Saran33/FiScrape/)

#### To install from git:
`pip install git+git://github.com/Saran33/FiScrape.git`
or
`git clone https://github.com/Saran33/FiScrape.git`

### Dependencies
FiScrape requires [Docker](https://docs.docker.com/desktop/), [Splash](https://splash.readthedocs.io/en/stable/install.html) and this fork of [Aquarium](https://github.com/Saran33/aquarium) to scrape some websites that render in Javascript.
1. After pip installing FiScrape, download Docker at the above link.
2. As per the above Splash installation docs, pull the splash image with:
##### Linux:
```zsh
$ sudo docker pull scrapinghub/splash
```
##### OS X / Windows:
```zsh
$ docker pull scrapinghub/splash
```
 3. Start the container:
##### Linux:
```zsh
$ sudo docker run -it -p 8050:8050 --rm scrapinghub/splash
```
(Splash is now available at 0.0.0.0 at port 8050 (http))
##### OS X / Windows:
```zsh
$ docker run -it -p 8050:8050 --rm scrapinghub/splash
```
(Splash is available at 0.0.0.0 address at port 8050 (http))
- Alternatively, use the Docker desktop app. Splash is found under the 'images' tab. Hover over it, click 'run'. In additional settings, name the container 'splash', and select a port such as 8050. Click 'run' and switch on the container before running scrapy. Switch it off after.
- In a browser, enter `localhost:8050` (or whatever port you choose), and you should see Splash is working.

- The other dependencies will be automatically installed and you can run FiScrape as normal.
 `$ sudo docker pull scrapinghub/splash` for Linux 
 or `$ docker pull scrapinghub/splash` for OS X.
 3. Aquarium creates multiple Splash instances behind a HAProxy, in order to load balance parallel scrapy requests to a splash docker cluster. The instances collaborate to render a specific website. It may be necessary for preventing 504 errors (timeout) on some sites. It also speeds up the scraping of Javascript pages, and can also facilitate Tor proxies. To install Aquarium, navigate to your home directory and run the command:
 ```zsh
 cookiecutter gh:Saran33/aquarium
 ```
 Choose default settings or whatever suits, splash_version: latest, set user and password, set Tor to 0.
 
 4. a. To start the container (without Acquarium):
 ##### Linux:
`$ sudo docker run -it --restart always -p 8050:8050 scrapinghub/splash` (Linux)
(Splash is now available at 0.0.0.0 at port 8050 (http).)
##### OS X / Windows:
or `$ docker run -it --restart always -p 8050:8050 scrapinghub/splash` (OS X)
(Splash is available at 0.0.0.0 address at port 8050 (http).)
- Alternatively, use the Docker desktop app. Splash is found in the 'images' tab. Hover over it, click 'run'. In additional settings, name the container 'splash', and select a port such as 8050. Click 'run.' 
- In a broweser, enter localhost:8050 (or whatever port you choose) and you should see Splash.
- The other dependencies will be automatically be installed and you can run FiScrape as normal.

4. b. Or to start the Splash cluster with Aquarium:

 Go to the new acquarium folder and start the Splash cluster:
 ```zsh
 cd ./aquarium
docker-compose up
 ```
In a browser window, visit the below link to view Splash is working:
http://localhost:8050/
To see the stats of the cluster:
http://localhost:8036/

### To run FiScrape:
#### To scrape all sites:
1. Navigate to the outer directory of FiScrape.
2. Open a terminal and run:
```zsh
python3 fiscrape.py 
```
#### To run FiScrape GUI:
```zsh
python3 fiscrape_gui.py
```
3. You will be prompted to enter a search term and the earliest publish date from which to scrape.
#### To scrape a specific site:
1. Navigate to the outer directory of FiScrape.
2. Open a terminal and run, for example, for the Financial Times:
```zsh
scrapy crawl ft
```
3. You will be prompted to enter a search term. e.g. ```Bitcoin```. You will then be prompted to enter the earliest date from which to scrape. e.g ```2021-01-15```. You can also enter ```t``` for today, ```yd``` for yesterday, ```w``` for the past week, ```m``` for month, or ```y``` for the start of the current year. For the matching articles returned from the query, each headline, standfirst (referring to the snippet on the site's search page), summary, image caption, content body, footnote, author name, author position, author bio, author email, author twitter, are returned to a database.
4. The default settings save the articles to a local SQLite database (which can be changed in settings.py). The DB can be read via SQL queries such as:
```zsh
sqlite3 FiScrape.db
.tables
.schema article
.schema sentiment
select * from article limit 3;
.quit
```
Alternatively, the DB can be opened in the convenient [DB Browser for SQLite](https://sqlitebrowser.org/).

To save the scraped data to a CSV as well as the DB, run:
```zsh
scrapy crawl ft -o output.csv -t csv
```

### To scrape the full HTML of a page:
Perform this test step in order to inspect a list of URLs, to see if they render in Javascript, or to simply scrape the raw HTML.
Save a csv file with a list of URLs. The column should be called 'URL' or 'url.'

Open a shell in the top level FiScrape dir. Run the following command and it will prompt you for the url path.
Enter ```d``` to read the default CSV file. The default CSV file can be changed in the "FiScrape/spiders/test_scr.py" file.
Enter ```t``` to read the default test CSV file. The test CSV file can be changed in the "FiScrape/spiders/test_scr.py" file.
```zsh
scrapy crawl test
```
or if you don't want to see the log:
```zsh
scrapy crawl test --nolog
```

### Sentiment Analysis
Additionally, FiScrape will return sentiment scores for each article's combined headline and standfirst, as well as seperate sentiment scores for the article's body. These sentiment scores will be stored in the database.
The default sentiment analysis pipeline calculates the following sentiment scores:

TextBlob (TextBlob is a Python Library based on the Natural Language ToolKit (NLTK)):
- `subjectivity` (A float, ranging between 0 and 1. 0 is objective and 1 is extremely subjective)
- `polarity` (A float, ranging between -1 and 1. -1 is extremely negative sentiment and 1 is extremely positive sentiment.

VADER (Valence Aware Dictionary and sEntiment Reasoning lexicon-based sentiment scores):
- compound (A composite score, calculated by summing the valence scores of each word in the lexicon, adjusted accordingly, then normalized between -1 and 1. -1 is extremely negative sentiment and 1 is extremely positive sentiment.
- `negative`
- `neutral`
- `positive`
The `negative`,`neutral` and `positive` scores are ratios describing the proportion of the text that falls into each category (so they should sum to 1, or close to it with floats).

### ML Pipeline Example
In the `NLP_Trading_Example.ipynb` notebook, there is an example of how to use either the Python libraries Pandas and SQLAlchemy to retrrieve the data. Pandas can accept SQL queries. The example function creates a temporary DB table of sentiment scores, for a given publication. It then uses the temp table to form a Pandas DataFrame. That function can be called recursively for each source/publication in the DB, to generate individual sentiment features for each source.

The example aggregates the data into hourly candles, for the purposes of illustration. That could be useful for generating lagged or resampled sentiment features, although that may not be necessay if using a model such as a LSTM neural network.

The notebook includes some trend indicators such as a Kalman filter, and volatility features such as Bollinger bands and a Yang-Zhang estimator. Numerous Python libraries need to be pip installed to run this file. Installing [Github-PWE_Analysis](https://github.com/Saran33/pwe_analysis/) should satisfy the dependencies. You will also need to install the C++ [TA-Lib](https://github.com/mrjbq7/ta-lib)

The data is then passed to a preprocessing pipeline. The categorical featues are converted to one-hot encodings and the rest of the features are scaled.

The example model is a basic Linear Discriminat Analysis classification model. This of course doesn't capture the sequential importance of features. The LDA is useful for dimensionality reduction though, so its outputs could be passed to a neural network.

Finally, the example contains a Backtrader backtesting environment, as well as Pyfolio analysis.
