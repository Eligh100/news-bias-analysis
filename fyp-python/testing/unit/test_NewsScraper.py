import os
from os import path
import boto3
import unittest
import feedparser
import time

from news_scraper.NewsScraper import NewsScraper
from helper_classes.Logger import Logger

class TestNewsScraper(unittest.TestCase):

    def setUp(self):

        # Establish AWS-related variables
        ACCESS_KEY_ID = "AKIASRO4ILWKGIB27HGU"
        SECRET_ACCESS_KEY = "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"

        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id = ACCESS_KEY_ID,
            aws_secret_access_key = SECRET_ACCESS_KEY
        )

        # Initialise log file, and logger
        self.log_path = "temp_files/testLog.txt"
        logger = Logger(self.log_path)

        # Initialise test data variables
        self.test_rss = "testing/unit/test_data/test_rss.xml"

        self.newsScraper = NewsScraper(dynamodb, logger)

    def test_scrapeArticles(self):
        # Arrange
        self.newsScraper.news_base_urls["GUARDIAN"] = [self.test_rss] # A saved RSS feed (to compare results)

        expected_urls = set([
            "https://www.theguardian.com/world/2020/apr/14/uk-care-providers-allege-covid-19-death-toll-underestimated",
            "https://www.theguardian.com/politics/2020/apr/14/antisemitism-inquiry-must-come-before-labour-officials-hired",
            "https://www.theguardian.com/business/2020/apr/14/how-close-is-the-nhs-to-getting-the-18000-ventilators-it-needs-coronavirus"
        ])

        # Act
        scraped_urls = self.newsScraper.scrapeArticles()

        # Assert
        self.assertEqual(expected_urls, scraped_urls["GUARDIAN"]) 
        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def test_checkArticleValidity(self):
        # Arrange
        entry = feedparser.parse(self.test_rss).entries[4]

        good_url = "https://www.theguardian.com/world/2020/apr/14/uk-care-providers-allege-covid-19-death-toll-underestimated"
        bad_url = "https://www.theguardian.com/commentisfree/picture/2020/apr/14/steve-bell-uk-care-homes-coronavirus-covid-19-cartoon"
        org_name = "GUARDIAN"

        # Act
        good_keywords_test = self.newsScraper.checkArticleValidity(entry, good_url, org_name)
        bad_keywords_test = self.newsScraper.checkArticleValidity(entry, bad_url, org_name)

        # Assert
        self.assertTrue(good_keywords_test)
        self.assertFalse(bad_keywords_test)
        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions


    def test_articleAlreadyStored(self):
        # Arrange
        existing_url = "https://www.bbc.co.uk/news/election-2019-50338070"
        not_existing_url = "https://www.theguardian.com/commentisfree/picture/2020/apr/14/steve-bell-uk-care-homes-coronavirus-covid-19-cartoon"

        # Act
        existing_url_test = self.newsScraper.articleAlreadyStored(existing_url)
        not_existing_url_test = self.newsScraper.articleAlreadyStored(not_existing_url)

        # Assert
        self.assertTrue(existing_url_test)
        self.assertFalse(not_existing_url_test)
        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def isLogEmpty(self):
        is_empty = False
        try:
            is_empty = os.stat(self.log_path).st_size == 0
        except:
            is_empty = not(path.exists(self.log_path))
        
        return is_empty

    def tearDown(self):

        # Delete any logs created
        try:
            os.remove(self.log_path)
        except:
            pass
