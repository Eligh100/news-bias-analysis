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
    """Scrapes articles from RSS feeds, and checks them for validity
        
    Arguments:
        dynamodb {Object} -- DynamoDB instance, to access DynamoDB tables
        logger {Logger} -- Logger instance, for logging exceptions
    """

    # Base RSS urls to fetch articles from
    news_base_urls = {
        "BBC": ["http://feeds.bbci.co.uk/news/politics/rss.xml"],
        "DAILY MAIL": ["https://www.dailymail.co.uk/news/uk-politics/index.rss", "https://www.dailymail.co.uk/news/general-election-2019/index.rss", "https://www.dailymail.co.uk/news/brexit/index.rss"],
        "DAILY MAIL ALL": ["https://www.dailymail.co.uk/articles.rss"],
        "GUARDIAN": ["https://www.theguardian.com/politics/rss"],
        "INDEPENDENT":["http://www.independent.co.uk/news/uk/politics/rss"],
        "TELEGRAPH": ["https://www.telegraph.co.uk/politics/rss.xml"], 
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

    # Stores when most recent update of article in database was
    curr_url_stored_time = datetime.datetime.now()

    def __init__(self, dynamodb, logger):
        self.dynamodb = dynamodb
        self.logger = logger

    def scrapeArticles(self):
        """Scrapes articles from RSS feeds, checks for validity, and returns valid article URLs
        
        Returns:
            {dict(string: [string])} -- Dictionary of key: news organisation and value: list of article URLs
        """

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
        """Checks article is valid, through a number of methods
        
        Arguments:
            entry {Object} -- RSS object of current entry in RSS file
            curr_url {string} -- URL being checked
            org_name {string} -- Name of current news organisation being processed
        
        Returns:
            {bool} -- Whether or not the article is valid 
        """

        keyword_dict = self.news_search_terms[org_name]

        updated_time = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))

        url_ok = False

        # Check the URL doesn't contain specific keywords
        # i.e. Guardian articles with /commentisfree/ are unwanted - just want articles
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
        """Checks whether an article is stored in the DynamoDB database
        
        Arguments:
            curr_url {string} -- URL being checked
        
        Returns:
            {bool} -- Whether or not article is already stored in the DynamoDB database
        """

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