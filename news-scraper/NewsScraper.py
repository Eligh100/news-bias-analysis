"""
News scraper - to scrape relevant articles for storage and further analysis

STEPS (per news org):

1. Go to base URL
2. Follow links to articles relating to UK politics (ignoring opinion pieces)
3. Get text content
4. Send to other script for trimming
"""

# BBC News - https://www.bbc.co.uk/news/election/2019   
#   URL will change after election, tool must be updated
# Daily mail - https://www.dailymail.co.uk/news/index.rss 
#   Won't need soup-ing
# Guardian -  https://www.theguardian.com/politics/rss 
#   Should I include opinion pieces?
#   Won't need soup-ing
#   If URL includes commentisfree, then an opinion piece
# Independent - http://www.independent.co.uk/news/uk/politics/rss 
# Mirror - https://www.mirror.co.uk/news/politics/
#   Will require soup-ing
# Telegraph - https://www.telegraph.co.uk/politics/
#   Will require soup-ing

# IMPORTS
import urllib3
import certifi
from bs4 import BeautifulSoup
import feedparser
from datetime import timedelta
import datetime
from time import mktime
import time

# TODO add logging for errors
class NewsScraper():

    news_search_terms = {}
    news_base_urls = {}
    news_filtered_urls = {}

    def __init__(self):
        
        # Base urls to fetch articles from - mixture of RSS and non-RSS
        self.news_base_urls = {
            "BBC": ["http://feeds.bbci.co.uk/news/politics/rss.xml"],
            "DAILY MAIL": ["https://www.dailymail.co.uk/news/uk-politics/index.rss", "https://www.dailymail.co.uk/news/general-election-2019/index.rss"],
            "GUARDIAN": ["https://www.theguardian.com/politics/rss"],
            "INDEPENDENT":["http://www.independent.co.uk/news/uk/politics/rss"],
            "TELEGRAPH": ["https://www.telegraph.co.uk/politics/"],
            "MIRROR": ["https://www.mirror.co.uk/news/politics/"],
        }

        # News org specific search terms, to filter out unwanted links
        self.news_search_terms = {
            "BBC": [["uk-politics","politics", "election-2019", "election"],["/live/","/correspondents/", "#comp-comments-button"]],
            "DAILY MAIL": [[],[]],
            "GUARDIAN": [[],["/commentisfree/", "/live/"]],
            "INDEPENDENT": [[],["/authors/"]],
            "TELEGRAPH": [["politics"],["/authors/","us-politics", "all-sections#politics"]],
            "MIRROR": [["politics/"],["/authors/", "#comments-section"]],
        }

        # URLs that are deemed relevant to the tool
        self.news_filtered_urls = {
            "BBC": set([]),
            "DAILY MAIL": set([]),
            "GUARDIAN": set([]),
            "INDEPENDENT": set([]),
            "TELEGRAPH": set([]),
            "MIRROR": set([]),
        }

    def scrapeArticles(self):
        for org_name, urls in self.news_base_urls.items():
            keyword_dict = self.news_search_terms[org_name]
            for url in urls:
                if ("rss" in url):
                    try:
                        rss_feed = feedparser.parse(url)  # TODO get authors and store w/ article - further analysis?
                    except:
                        print("Link failed - check url validity: " + url)
                    else:
                        for entry in rss_feed.entries:
                            for curr_url in entry.links:
                                if (curr_url.type == "text/html" ): # ignore images and other media

                                    published_time = datetime.datetime.fromtimestamp(mktime(entry.published_parsed))
                                    updated_time = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))
                                    week_prior = datetime.datetime.now() - timedelta(days=7)

                                    href_url = curr_url.href

                                    url_ok = False

                                    if (keyword_dict[0] == [] and not any(keyword in href_url for keyword in keyword_dict[1])):
                                        url_ok = True
                                    elif (any(keyword in href_url for keyword in keyword_dict[0]) and not any(keyword in href_url for keyword in keyword_dict[1])):
                                        url_ok = True
                                
                                    if (url_ok):

                                        if (updated_time > published_time):
                                            self.checkForDatabaseUpdate(href_url)

                                        if (published_time >= week_prior): # only consider articles from one week ago (mostly important for first run of tool)
                                            self.news_filtered_urls[org_name].add(href_url)
                else:
                    try:
                        response = urllib3.PoolManager(
                            cert_reqs='CERT_REQUIRED',
                            ca_certs=certifi.where()
                        ).request('GET', url)

                        soup = BeautifulSoup(response.data, 'html.parser')
                    except:
                        print("Link failed - check url validity: " + url)
                    else:
                        for link in soup.find_all('a'):
                            curr_url = link.get('href')
                            if (curr_url != None):
                                if (any(keyword in curr_url for keyword in keyword_dict[0]) and not any(keyword in curr_url for keyword in keyword_dict[1])):
                                    if (org_name == "BBC"):
                                        if ("https://www.bbc.co.uk" not in curr_url): # TODO move this
                                            curr_url = "https://www.bbc.co.uk" + curr_url
                                    elif (org_name == "TELEGRAPH"):
                                        if ("https://www.telegraph.co.uk" not in curr_url):
                                            curr_url = "https://www.telegraph.co.uk" + curr_url
                                    self.news_filtered_urls[org_name].add(curr_url)

        return self.news_filtered_urls
        
    def checkForDatabaseUpdate(self, curr_url):
        x = 1
        # TODO 
        # Check database for url
        # If in database, check timestamp
        # If different, update with new text
    