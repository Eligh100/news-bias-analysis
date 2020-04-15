import os
from os import path
import unittest

from news_scraper.ArticleTrimmer import ArticleTrimmer
from helper_classes.Logger import Logger

class TestNewsScraper(unittest.TestCase):

    def setUp(self):

        # Initialise log file, and logger
        self.log_path = "temp_files/testLog.txt"
        logger = Logger(self.log_path)

        # Initialise test data variables

        self.articleTrimmer = ArticleTrimmer(logger)

    def test_trimArticle(self):
        # Arrange
        bad_daily_mail_url = "https://www.dailymail.co.uk/sport/football/article-8213779/Why-Premier-League-transfer-deals-fall-summer-amid-1-8BILLION-drop-value.html"
        
        good_url_1 = "https://www.theguardian.com/politics/2019/dec/03/labour-plan-to-tackle-rip-off-britain-would-save-families-6700"

        expected_article_text_1 = open("testing/unit/test_data/good_article_text_1.txt", "r", encoding="utf-8").read()
        expected_headline_1 = "Labour plan to tackle 'rip-off Britain would save families £6,700'"
        expected_author_1 = "Heather Stewart"
        expected_pub_date_1 = "03 December 2019"

        good_url_2 = "https://www.independent.co.uk/news/uk/home-news/terror-laws-jail-indefinitely-streatham-attack-a9315651.html"

        expected_article_text_2 = open("testing/unit/test_data/good_article_text_2.txt", "r", encoding="utf-8").read()
        expected_headline_2 = "Terror offenders could be jailed indefinitely under government proposals after Streatham attack"
        expected_author_2 = "Lizzie Dearden, Andrew Woodcock"
        expected_pub_date_2 = "03 February 2020"

        test_articles = {
            "DAILY MAIL ALL": [bad_daily_mail_url],
            "GUARDIAN": [good_url_1],
            "INDEPENDENT": [good_url_2]
        }

        # Act
        test_results = self.articleTrimmer.trimArticle(test_articles)

        # Assert
        self.assertNotIn(bad_daily_mail_url, test_results)
        self.assertIn(good_url_1, test_results)
        self.assertIn(good_url_2, test_results)
        
        # For good_url_1
        good_url_1_results = test_results[good_url_1]
        self.assertEqual(expected_article_text_1, good_url_1_results[0])
        self.assertEqual(expected_headline_1, good_url_1_results[1])
        self.assertEqual(expected_author_1, good_url_1_results[2])
        self.assertEqual(expected_pub_date_1, good_url_1_results[4])

        # For good_url_2
        good_url_2_results = test_results[good_url_2]
        self.assertEqual(expected_article_text_2, good_url_2_results[0])
        self.assertEqual(expected_headline_2, good_url_2_results[1])
        self.assertEqual(expected_author_2, good_url_2_results[2])
        self.assertEqual(expected_pub_date_2, good_url_2_results[4])

    def isLogEmpty(self):
        is_empty = False
        try:
            is_empty = os.stat(self.log_path).st_size == 0
        except:
            is_empty = path.exists(self.log_path)
        
        return is_empty

    def tearDown(self):

        # Delete any logs created
        try:
            os.remove(self.log_path)
        except:
            pass
