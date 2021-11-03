# TickerScrape
![alt text](https://github.com/Saran33/TickerScrape/blob/main/images/PWE_TickerScrape_splash.png?raw=true)
### Scrape the universe of exchange-traded security tickers. 
`TickerScrape` is a package for scraping financial security ticker data. It leverages `scrapy`.

Tickers can be stored locally as CSV or in a database using SQLAlchemy. The scraper can be set to run periodically.

The repository can be found at:
[Github-TickerScrape](https://github.com/Saran33/TickerScrape/)

#### To install from git:
`pip install git+git://github.com/Saran33/TickerScrape.git`
or
`git clone https://github.com/Saran33/TickerScrape.git`

### Dependencies
TickerScrape requires [Docker](https://docs.docker.com/desktop/), [Splash](https://splash.readthedocs.io/en/stable/install.html) and this fork of [Aquarium](https://github.com/Saran33/aquarium) to scrape some websites that render in Javascript.
1. After pip installing TickerScrape, download Docker at the above link.
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

- The other dependencies will be automatically installed and you can run TickerScrape as normal.
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
- The other dependencies will be automatically be installed and you can run TickerScrape as normal.

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

### To run TickerScrape:
1. Navigate to the outer directory of TickerScrape.
2. Open a terminal and run:
```zsh
python3 TickerScrape.py 
```
#### To run TickerScrape GUI:
```zsh
python3 TickerScrape_gui.py
```
3. The default settings save the tickers to a local SQLite database (which can be changed in settings.py). The DB can be read via SQL queries such as:
```zsh
sqlite3 TickerScrape.db
.tables
.schema stocks
.schema bonds
select * from stocks limit 3;
.quit
```
Alternatively, the DB can be opened in the convenient [DB Browser for SQLite](https://sqlitebrowser.org/).

To save the scraped data to a CSV as well as the DB, run:
```zsh
scrapy crawl marketwatch -o output.csv -t csv
```
