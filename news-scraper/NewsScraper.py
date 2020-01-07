"""
News scraper - to scrape relevant articles for storage and further analysis

STEPS (per news org):

1. Go to base URL
2. Follow links to articles relating to UK politics (ignoring opinion pieces)
3. Get text content
4. Send to other script for trimming
""" # TODO update this

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

    # Base urls to fetch articles from - mixture of RSS and non-RSS
    news_base_urls = {
        "BBC": ["http://feeds.bbci.co.uk/news/politics/rss.xml"],
        "DAILY MAIL": ["https://www.dailymail.co.uk/news/uk-politics/index.rss", "https://www.dailymail.co.uk/news/general-election-2019/index.rss"],
        "GUARDIAN": ["https://www.theguardian.com/politics/rss"],
        "INDEPENDENT":["http://www.independent.co.uk/news/uk/politics/rss"],
        "TELEGRAPH": ["https://www.telegraph.co.uk/politics/rss.xml"],
        "MIRROR": ["https://www.mirror.co.uk/news/politics/?service=rss"],
    }

    # News org specific search terms, to filter out unwanted links
    news_search_terms = {
        "BBC": [["uk-politics","politics", "election-2019", "election"],["/live/","/correspondents/", "#comp-comments-button"]],
        "DAILY MAIL": [[],[]],
        "GUARDIAN": [[],["/commentisfree/", "/live/"]],
        "INDEPENDENT": [[],["/authors/"]],
        "TELEGRAPH": [["politics"],["/authors/","us-politics", "all-sections#politics"]],
        "MIRROR": [["politics/"],["/authors/", "#comments-section"]],
    }

    # URLs that are deemed relevant to the tool
    news_filtered_urls = {
        "BBC": set([]),
        "DAILY MAIL": set([]),
        "GUARDIAN": set([]),
        "INDEPENDENT": set([]),
        "TELEGRAPH": set([]),
        "MIRROR": set([]),
    }

    curr_url_stored_time = datetime.datetime.now()

    dynamodb = ""

    def __init__(self, dynamodb):

        self.dynamodb = dynamodb

    def scrapeArticles(self):
        for org_name, urls in self.news_base_urls.items():
            for url in urls:
                try:
                    rss_feed = feedparser.parse(url) 
                except:
                    print("Link failed - check url validity: " + url)
                else:
                    for entry in rss_feed.entries:
                        for curr_url in entry.links:
                            if (curr_url.type == "text/html" ): # ignore images and other media

                                href_url = curr_url.href

                                articleValid = self.checkArticleValidity(entry, href_url, org_name)

                                if (articleValid):
                                    self.news_filtered_urls[org_name].add(href_url)

        return self.news_filtered_urls

    def checkArticleValidity(self, entry, curr_url, org_name):
        keyword_dict = self.news_search_terms[org_name]

        published_time = datetime.datetime.fromtimestamp(mktime(entry.published_parsed))
        updated_time = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))
        week_prior = datetime.datetime.now() - timedelta(days=7)

        url_ok = False

        if (keyword_dict[0] == [] and not any(keyword in curr_url for keyword in keyword_dict[1])):
            url_ok = True
        elif (any(keyword in curr_url for keyword in keyword_dict[0]) and not any(keyword in curr_url for keyword in keyword_dict[1])):
            url_ok = True

        if (url_ok):

            # Check if article already in the table
            # If not, check it's not a week old (via published or updated time)
            # If so, see if the updated time > time in database

            if (self.articleAlreadyStored(curr_url)):
                if (updated_time > self.curr_url_stored_time): # more recent version of article available
                    return True
                else:
                    return False # ignore already stored articles
            else:
                if (published_time >= week_prior or updated_time >= week_prior): # only consider articles from one week ago (mostly important for first run of tool)
                    return True
    
    def articleAlreadyStored(self, curr_url):
        table = self.dynamodb.Table('Articles-Table')

        try:
            response = table.get_item(
                Key={
                    'article-url': curr_url,
                }
            )
        except:
            return False
        else:
            item = response['Item']
            self.curr_url_stored_time = datetime.datetime.strptime(item["most-recent-update"], "%d/%m/%Y, %H:%M:%S")
            return True
    