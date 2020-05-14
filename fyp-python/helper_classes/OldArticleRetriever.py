# Guardian
#   https://www.theguardian.com/politics?page=175
#   https://www.theguardian.com/politics?page=65
# Mirror
#   https://www.google.co.uk/search?q=site:https://www.mirror.co.uk/news/politics/&tbs=sbd:1,cdr:1,cd_min:11/10/2019,cd_max:1/7/2020&tbm=nws&sxsrf=ALeKk00BiubT5lDKD1jd8bgD7Tc1z2fbFA:1582569838735&ei=bhlUXuu8LLim1fAP-6q50Ag&start=0&sa=N&ved=0ahUKEwjrq8eI7OrnAhU4UxUIHXtVDoo4yAEQ8tMDCPcE&biw=1536&bih=722&dpr=1.25
# BBC
#   https://www.google.com/search?q=site:bbc.co.uk+bbc+news+%22uk-politics%22%7C%22election-2019%22&tbs=cdr:1,cd_min:11/10/2019,cd_max:1/10/2020&tbm=nws&sxsrf=ALeKk026GQb1MyhFgalOXG8prnWwk3NM-Q:1582569961613&ei=6RlUXtODJY2Q8gKc7o3IDg&start=0&sa=N&ved=0ahUKEwiTnJPD7OrnAhUNiFwKHRx3A-k4yAEQ8tMDCEk&biw=1536&bih=722&dpr=1.25
# Independent
#   https://www.google.co.uk/search?q=https://www.independent.co.uk/news/uk/politics&tbs=cdr:1,cd_min:11/10/2019,cd_max:1/7/2020,sbd:1&tbm=nws&sxsrf=ALeKk03JghhECFhT0_910yWJIEy36tUy1g:1582570083663&source=lnt&sa=X&ved=0ahUKEwi7wKz97OrnAhWmVBUIHRDjATwQpwUIIA&biw=1536&bih=722&dpr=1.25
# Daily Mail
#   https://www.google.co.uk/search?biw=1536&bih=722&tbs=cdr%3A1%2Ccd_min%3A11%2F10%2F2019%2Ccd_max%3A1%2F7%2F2020%2Csbd%3A1&tbm=nws&sxsrf=ALeKk00ysLzoATiA-Ma0eNbE4pkVK_mJSA%3A1582570232146&ei=-BpUXvi-CMmc1fAP-dCZ6A8&q=site%3Ahttps%3A%2F%2Fwww.dailymail.co.uk%2Fnews%2F&oq=site%3Ahttps%3A%2F%2Fwww.dailymail.co.uk%2Fnews%2F&gs_l=psy-ab.3...254970.255649.0.256001.5.5.0.0.0.0.106.399.3j2.5.0....0...1c.1.64.psy-ab..0.0.0....0.GHC-pYdy2Ps


# Use this class instead of NewsScraper.py - send filtered urls to ArticleTrimmer -> ArticleUploader

import requests
import re
import time
from time import mktime
from datetime import timedelta
import datetime
import boto3
import json
from bs4 import BeautifulSoup
from serpwow.google_search_results import GoogleSearchResults

class OldArticleRetriever:

    google_search_urls = {
        # "BBC": ["site:bbc.co.uk/news/uk-politics", "site:bbc.co.uk/news/election-2019"],
        # "DAILY MAIL ALL": ["site:https://www.dailymail.co.uk/news/"],
        # "INDEPENDENT": ["site:https://www.independent.co.uk/news/uk/politics"],
        "MIRROR": ["site:https://www.mirror.co.uk/news/politics/"],
        "TELEGRAPH": ["site:https://www.telegraph.co.uk/politics/"]
    }

    google_search_pages = {
        # "BBC": [1, 3],
        # "DAILY MAIL ALL": [4],
        # "INDEPENDENT": [3],
        "MIRROR": [4],
        "TELEGRAPH": [4]
    }

    base_urls = {
        # "BBC" : ["https://www.bbc.co.uk/news/uk-politics", "https://www.bbc.co.uk/news/election-2019", "election-2019", "uk-politics"],
        # "DAILY MAIL ALL": ["https://www.dailymail.co.uk/news/article", "dailymail"],
        # "INDEPENDENT": ["https://www.independent.co.uk/news/uk/politics", "independent"],
        "MIRROR": ["https://www.mirror.co.uk/news/politics", "mirror"],
        "TELEGRAPH":["https://www.telegraph.co.uk/politics/", "telegraph"]
        #"GUARDIAN": ["https://www.theguardian.com/politics", "guardian"]
    }

    news_filtered_urls = {
        # "BBC": set([]),
        # "DAILY MAIL ALL": set([]),
        # "INDEPENDENT": set([]),
        "MIRROR": set([]),
        #"GUARDIAN": set([]),
        "TELEGRAPH": set([])
    }

    news_search_terms = {
        # "BBC": ["/live/","/correspondents/", "#comp-comments-button", "accounts.google.com"],
        # "DAILY MAIL ALL": ["accounts.google.com"],
        #"GUARDIAN": ["/commentisfree/", "/live/", "/all", "accounts.google.com"],
        # "INDEPENDENT": ["/authors/", "accounts.google.com"],
        "MIRROR": ["/authors/", "#comments-section", "accounts.google.com"],
        "TELEGRAPH": ["/authors/","us-politics", "all-sections#politics", "accounts.google.com"],
    }

    base_guardian = "https://www.theguardian.com/politics?"
    guardian_start_page = "https://www.theguardian.com/politics?page=1"
    guardian_end_page = "https://www.theguardian.com/politics?page=32"

    def __init__(self, dynamodb, logger):
        self.dynamodb = dynamodb
        self.logger = logger

        # create the serpwow object, passing in our API key
        self.serpwow = GoogleSearchResults("6367BDFAE2D847088B91A8312CD6BA4C")

    def getOldArticles(self):

        # Get articles for all (but Guardian)
        for org_name, google_urls in self.google_search_urls.items():
            keywords_list = self.news_search_terms[org_name]
            counter = -1
            for google_url in google_urls:
                counter +=1
                num_of_pages = self.google_search_pages[org_name][counter]

                current_page = 0
                while (current_page != num_of_pages):
                    current_page += 1

                    # set up a dict for the search parameters, retrieving results as JSON
                    params = {
                        "q" : google_url,
                        "gl" : "us",
                        "hl" : "en",
                        "google_domain" : "google.com",
                        "time_period" : "custom",
                        "sort_by" : "date",
                        "time_period_min" : "03/28/2020",
                        "time_period_max" : "05/13/2020",
                        "page" : str(current_page),
                        "num" : "100"
                    }

                    result_page = self.serpwow.get_json(params)

                    for link_json in result_page["organic_results"]:
                        link = link_json["link"]

                        if any(x in link for x in self.base_urls[org_name]):
                            url_ok = False
                            if keywords_list == []:
                                url_ok = True
                            elif not any(keyword in link for keyword in keywords_list):
                                url_ok = True
                                
                            if (url_ok):
                                try:
                                    test_request = requests.get(link)
                                except: # if this fails, link is bad, ignore
                                    continue

                                if (self.articleAlreadyStored(link)):
                                    continue
                                else:
                                    self.news_filtered_urls[org_name].add(link)


        # # Get guardian articles
        # keywords_list = self.news_search_terms["GUARDIAN"]
        # current_url = self.guardian_start_page
        # while(current_url != self.guardian_end_page):
        #     result = re.search(r'(page=)(.*)', current_url)
        #     next_page_num = int(result.group(2)) + 1
        #     current_url = self.base_guardian + "page=" + str(next_page_num)

        #     response = requests.get(current_url)
        #     print(response.status_code)
        #     soup = BeautifulSoup(response.text, 'html.parser')

        #     for link in soup.find_all('a'):
        #         url = link.get('href')
                
        #         try: # try because url can be None
        #             if any(x in url for x in self.base_urls["GUARDIAN"]):
        #                 url_ok = False
        #                 if not any(keyword in url for keyword in keywords_list):
        #                     url_ok = True

        #                 if (url_ok):
        #                     try:
        #                         test_request = requests.get(url)
        #                     except:
        #                         continue
        #                     if (self.articleAlreadyStored(url)):
        #                         continue
        #                     else:
        #                         self.news_filtered_urls["GUARDIAN"].add(url)
        #         except:
        #             continue

        return self.news_filtered_urls

        
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
    



