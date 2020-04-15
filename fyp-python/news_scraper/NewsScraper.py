"""
News scraper - to scrape relevant articles for storage and further analysis

STEPS (per news org):

1. Go to base URL
2. Follow links to articles relating to UK politics (ignoring opinion pieces)
3. Get text content
4. Send to other script for trimming
""" # TODO update this

# IMPORTS
import urllib3
import certifi
from bs4 import BeautifulSoup
import feedparser
from datetime import timedelta
import datetime
from time import mktime
import time
import boto3

class NewsScraper():

    # Base RSS urls to fetch articles from
    news_base_urls = {
        "BBC": ["http://feeds.bbci.co.uk/news/politics/rss.xml"],
        "DAILY MAIL": ["https://www.dailymail.co.uk/news/uk-politics/index.rss", "https://www.dailymail.co.uk/news/general-election-2019/index.rss", "https://www.dailymail.co.uk/news/brexit/index.rss"],
        "DAILY MAIL ALL": ["https://www.dailymail.co.uk/articles.rss"],
        "GUARDIAN": ["https://www.theguardian.com/politics/rss"],
        "INDEPENDENT":["http://www.independent.co.uk/news/uk/politics/rss"],
        "TELEGRAPH": ["https://www.telegraph.co.uk/politics/rss.xml"], # TODO telegraph has paywall - note this as reason for less articles
        "MIRROR": ["https://www.mirror.co.uk/news/politics/?service=rss"],
    }

    # News org specific search terms, to filter out unwanted links
    news_search_terms = {
        "BBC": [["uk-politics","politics", "election-2019", "election"],["/live/","/correspondents/", "#comp-comments-button"]],
        "DAILY MAIL": [[],[]],
        "DAILY MAIL ALL": [[],[]],
        "GUARDIAN": [[],["/commentisfree/", "/live/"]],
        "INDEPENDENT": [[],["/authors/"]],
        "TELEGRAPH": [["politics"],["/authors/","us-politics", "all-sections#politics"]],
        "MIRROR": [["politics/"],["/authors/", "#comments-section"]],
    }

    # URLs that are deemed relevant to the tool
    news_filtered_urls = {
        "BBC": set([]),
        "DAILY MAIL": set([]),
        "DAILY MAIL ALL": set([]),
        "GUARDIAN": set([]),
        "INDEPENDENT": set([]),
        "TELEGRAPH": set([]),
        "MIRROR": set([]),
    }

    curr_url_stored_time = datetime.datetime.now()

    dynamodb = ""
    logger = ""

    def __init__(self, dynamodb, logger):

        self.dynamodb = dynamodb
        self.logger = logger

    def scrapeArticles(self):
        for org_name, urls in self.news_base_urls.items():
            for url in urls:
                try:
                    rss_feed = feedparser.parse(url) 
                except Exception as e:
                    log_line = "Link failed - check url validity: " + url
                    log_line += "\nFailed with following exception:\n"
                    log_line += str(e)
                    log_line += "\n"
                    self.logger.writeToLog(log_line, False)
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

        updated_time = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))

        url_ok = False

        if (keyword_dict[0] == [] and not any(keyword in curr_url for keyword in keyword_dict[1])):
            url_ok = True
        elif (any(keyword in curr_url for keyword in keyword_dict[0]) and not any(keyword in curr_url for keyword in keyword_dict[1])):
            url_ok = True

        if (url_ok):

            # Check if article already in the table
            # If so, see if the updated time > time in database

            if (self.articleAlreadyStored(curr_url)):
                if (updated_time > self.curr_url_stored_time): # more recent version of article available
                    return True
                else:
                    return False # ignore already stored articles
            else:
                return True
    
    def articleAlreadyStored(self, curr_url):
        table = self.dynamodb.Table('Articles-Table') 

        try:
            response = table.get_item(
                Key={
                    'article-url': curr_url
                }
            )
        except Exception as e:
            log_line = "Failed to access DynamoDB table: Articles-Table with following exception:\n"
            log_line += str(e)
            self.logger.writeToLog(log_line, False)
            log_line = "Exited prematurely at: "
            self.logger.writeToLog(log_line, True)
            exit(0)
        else:
            try:
                item = response['Item']
            except:
                return False # no item means article doesn't exist in database
            else:
                self.curr_url_stored_time = datetime.datetime.strptime(item["most-recent-update"], "%d/%m/%Y, %H:%M:%S")
                return True