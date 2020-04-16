import os
from os import path
import unittest
import numpy as np
import boto3
import re

from sentiment_processor.ArticleUploader import ArticleUploader
from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor
from helper_classes.Enums import PoliticalPartyHelper 

class TestArticleUploader(unittest.TestCase):

    def setUp(self):

        # Establish AWS-related variables
        bucket_name = "articles-text"
        ACCESS_KEY_ID = "AKIASRO4ILWKGIB27HGU"
        SECRET_ACCESS_KEY = "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"

        s3 = boto3.resource(
            's3',
            aws_access_key_id = ACCESS_KEY_ID,
            aws_secret_access_key = SECRET_ACCESS_KEY
            )

        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id = ACCESS_KEY_ID,
            aws_secret_access_key = SECRET_ACCESS_KEY
            )

        table = dynamodb.Table('Articles-Table')

        # Initialise log file, and logger
        self.log_path = "temp_files/testLog.txt"
        logger = Logger(self.log_path)
        
        # Initialise test data variables
        self.article_url = "https://www.testurl.co.uk/dummy/dummy2"

        article_text = "Test text line 1\nTest text line 2"
        article_headline = "Test Headline: A headline for testing"
        article_author = "Test Author"
        org_name = "Test org"
        article_pub_date = "Test pub date"

        self.article_data = [article_text, article_headline, article_author, org_name, article_pub_date]

        likely_topics = np.array([1, 5])
        likely_parties = np.array([1, 4])

        article_topic_sentiment_matrix =  { 1: -1, 5: 0.6 }
        article_party_sentiment_matrix = { 1: 1, 4: -0.8 }

        most_similar_party = PoliticalPartyHelper.PoliticalParty.labour

        headline_topics_sentiment_matrix = { } # Empty to test if set to 'NO INFO' when encoded to string
        headline_parties_sentiment_matrix = { 1: 1 }

        top_words = { "test1": 1, "test2": 2, "test3": 3, "test4": 4, "test5": 5, "test6": 6, "test7": 7, "test8": 8, "test9": 9, "test10": 10, "test11": 11,
         "test12": 12, "test13": 13, "test14": 14, "test15": 15, "test16": 16, "test17": 17, "test18": 18, "test19": 19, "test20": 20 }

        self.articleUploader = ArticleUploader(s3, bucket_name, table, logger, likely_topics, likely_parties, article_topic_sentiment_matrix, article_party_sentiment_matrix,
            most_similar_party, headline_topics_sentiment_matrix, headline_parties_sentiment_matrix, top_words)

    def test_uploadArticles(self):
        # Arrange
        sanitised_url = "www.testurl.co.ukFYPSLASHFYPdummyFYPSLASHFYPdummy2.txt"
        expected_s3_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(
                "articles-text",
                "eu-west-2",
                sanitised_url)

        expected_text = self.article_data[0]
        expected_author = self.article_data[2]
        expected_headline = self.article_data[1]
        expected_org = self.article_data[3]
        expected_pub_date = self.article_data[4]
        expected_parties = "Labour, SNP"
        expected_party_sentiments = "Labour = 1, SNP = -0.8"
        expected_topic_sentiments = "Scotland = -1, Economy/Business = 0.6"
        expected_topics = "Scotland, Economy/Business"
        expected_headline_party_sentiments = "Labour = 1"
        expected_headline_topic_sentiments = "NO INFO"
        expected_likely_party = "Labour"
        expected_top_words = "test1 = 1, test2 = 2, test3 = 3, test4 = 4, test5 = 5, test6 = 6, test7 = 7, test8 = 8, test9 = 9, test10 = 10, test11 = 11, test12 = 12, test13 = 13, test14 = 14, test15 = 15, test16 = 16, test17 = 17, test18 = 18, test19 = 19, test20 = 20"

        # Act
        self.articleUploader.uploadArticles(self.article_url, self.article_data)

        response = self.articleUploader.table.get_item(
            Key={
                'article-url': self.article_url
            }
        )

        # Assert
        try:
            item = response['Item']
        except: # Always fail test if item wasn't stored in database
            self.assertTrue(False) 
        else:
            # Assert contents of database are correct
            self.assertEqual(expected_author, item["article-author"])
            self.assertEqual(expected_headline, item["article-headline"])
            self.assertEqual(expected_org, item["article-org"])
            self.assertEqual(expected_parties, item["article-parties"])
            self.assertEqual(expected_party_sentiments, item["article-party-sentiments"])
            self.assertEqual(expected_pub_date, item["article-pub-date"])
            self.assertEqual(expected_s3_url, item["article-text"])
            self.assertEqual(expected_topic_sentiments, item["article-topic-sentiments"])
            self.assertEqual(expected_topics, item["article-topics"])
            self.assertEqual(expected_headline_party_sentiments, item["headline-party-sentiments"])
            self.assertEqual(expected_headline_topic_sentiments, item["headline-topic-sentiments"])
            self.assertEqual(expected_likely_party, item["most-likely-party"])
            self.assertEqual(expected_top_words, item["top-words"])

            # Assert article text has been stored properly
            s3_url = item["article-text"]

            # Download article text and save as .txt
            s3_object_filename = (s3_url.split("amazonaws.com/"))[1]
            # Get rid of anything after .txt
            trimmed = s3_object_filename.split(".txt")[0] + ".txt"
            trimmed = re.sub(r'[/\\:*?"<>|]', '', trimmed)
            local_filename = 'testing/unit/test_data/' + trimmed
            self.articleUploader.s3.Bucket(self.articleUploader.bucket_name).download_file(s3_object_filename, local_filename)

            with open(local_filename, "r", encoding="utf-8") as test_file:
                self.assertEqual(expected_text, test_file.read())

            self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

            # Cleanup

            # Delete S3 object
            self.articleUploader.s3.Object(self.articleUploader.bucket_name,sanitised_url).delete()

            # Check item has been deleted
            try:
                self.articleUploader.s3.Object(self.articleUploader.bucket_name, sanitised_url).load()
            except:
                pass
            else:
                self.assertTrue(False) # Fail test if S3 object deletion fails

            # Delete DynamoDB item
            try:
                self.articleUploader.table.delete_item(
                    Key={
                        'article-url': self.article_url
                    }
                )
            except:
                self.assertTrue(False)
            else:
                # Check item has been deleted
                response = self.articleUploader.table.get_item(
                    Key={
                        'article-url': self.article_url
                    }
                )

                try:
                    item = response['Item']
                except:
                    pass
                else:
                    self.assertTrue(False)

    def test_sanitiseURL(self):
        # Arrange
        expected_url = "www.testurl.co.ukFYPSLASHFYPdummyFYPSLASHFYPdummy2.txt"

        # Act
        actual_url = self.articleUploader.sanitiseURL(self.article_url)

        # Assert
        self.assertEqual(expected_url, actual_url)

    def test_getS3Url(self):
        # Arrange
        sanitised_url = "www.testurl.co.ukFYPSLASHFYPdummyFYPSLASHFYPdummy2.txt"
        expected_s3_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(
                "articles-text",
                "eu-west-2",
                sanitised_url)
        
        # Act
        actual_s3_url = self.articleUploader.getS3Url(sanitised_url)

        # Assert
        self.assertEqual(expected_s3_url, actual_s3_url)
        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def test_encodeDataToString(self):
        # Arrange
        expected_likely_topics = "Scotland, Economy/Business"
        expected_likely_parties = "Labour, SNP"
        expected_article_topic_sentiment_matrix = "Scotland = -1, Economy/Business = 0.6"
        expected_article_party_sentiment_matrix = "Labour = 1, SNP = -0.8"
        expected_most_similar_party = "Labour"
        expected_headline_topics_sentiment_matrix = "NO INFO"
        expected_headline_parties_sentiment_matrix = "Labour = 1"
        expected_top_words = "test1 = 1, test2 = 2, test3 = 3, test4 = 4, test5 = 5, test6 = 6, test7 = 7, test8 = 8, test9 = 9, test10 = 10, test11 = 11, test12 = 12, test13 = 13, test14 = 14, test15 = 15, test16 = 16, test17 = 17, test18 = 18, test19 = 19, test20 = 20"

        # Act
        self.articleUploader.encodeDataToString()

        # Assert
        self.assertEqual(expected_likely_topics, self.articleUploader.likely_topics)
        self.assertEqual(expected_likely_parties, self.articleUploader.likely_parties)
        self.assertEqual(expected_article_topic_sentiment_matrix, self.articleUploader.article_topic_sentiment_matrix)
        self.assertEqual(expected_article_party_sentiment_matrix, self.articleUploader.article_party_sentiment_matrix)
        self.assertEqual(expected_most_similar_party, self.articleUploader.most_similar_party)
        self.assertEqual(expected_headline_topics_sentiment_matrix, self.articleUploader.headline_topics_sentiment_matrix)
        self.assertEqual(expected_headline_parties_sentiment_matrix, self.articleUploader.headline_parties_sentiment_matrix)
        self.assertEqual(expected_top_words, self.articleUploader.top_words)

    def test_updateDatabase(self):
        # Arrange
        sanitised_url = "www.testurl.co.ukFYPSLASHFYPdummyFYPSLASHFYPdummy2.txt"
        expected_s3_url = "testS3URL"

        expected_text = self.article_data[0]
        expected_author = self.article_data[2]
        expected_headline = self.article_data[1]
        expected_org = self.article_data[3]
        expected_pub_date = self.article_data[4]
        expected_parties = "Labour, SNP"
        expected_party_sentiments = "Labour = 1, SNP = -0.8"
        expected_topic_sentiments = "Scotland = -1, Economy/Business = 0.6"
        expected_topics = "Scotland, Economy/Business"
        expected_headline_party_sentiments = "Labour = 1"
        expected_headline_topic_sentiments = "NO INFO"
        expected_likely_party = "Labour"
        expected_top_words = "test1 = 1, test2 = 2, test3 = 3, test4 = 4, test5 = 5, test6 = 6, test7 = 7, test8 = 8, test9 = 9, test10 = 10, test11 = 11, test12 = 12, test13 = 13, test14 = 14, test15 = 15, test16 = 16, test17 = 17, test18 = 18, test19 = 19, test20 = 20"

        # Act
        self.articleUploader.encodeDataToString()
        self.articleUploader.updateDatabase(self.article_url, self.article_data, expected_s3_url)

        response = self.articleUploader.table.get_item(
            Key={
                'article-url': self.article_url
            }
        )

        # Assert
        try:
            item = response['Item']
        except: # Always fail test if item wasn't stored in database
            self.assertTrue(False) 
        else:
            # Assert contents of database are correct
            self.assertEqual(expected_author, item["article-author"])
            self.assertEqual(expected_headline, item["article-headline"])
            self.assertEqual(expected_org, item["article-org"])
            self.assertEqual(expected_parties, item["article-parties"])
            self.assertEqual(expected_party_sentiments, item["article-party-sentiments"])
            self.assertEqual(expected_pub_date, item["article-pub-date"])
            self.assertEqual(expected_s3_url, item["article-text"])
            self.assertEqual(expected_topic_sentiments, item["article-topic-sentiments"])
            self.assertEqual(expected_topics, item["article-topics"])
            self.assertEqual(expected_headline_party_sentiments, item["headline-party-sentiments"])
            self.assertEqual(expected_headline_topic_sentiments, item["headline-topic-sentiments"])
            self.assertEqual(expected_likely_party, item["most-likely-party"])
            self.assertEqual(expected_top_words, item["top-words"])

            # Now, test updating of item (used when an article is updated - same URL/key, different content)
            expected_likely_party = "SNP"
            expected_headline = "Test Headline 2: Another headline for testing"
            new_s3_url = "newTestS3URL"

            self.articleUploader.most_similar_party = expected_likely_party
            self.article_data[1] = expected_headline

            # Act again
            self.articleUploader.updateDatabase(self.article_url, self.article_data, new_s3_url)

            response = self.articleUploader.table.get_item(
                Key={
                    'article-url': self.article_url
                }
            )

            # Assert updating of the item worked
            try:
                item = response['Item']
            except: # Always fail test if item wasn't stored in database
                self.assertTrue(False) 
            else:
                # Assert contents of database are correct
                self.assertEqual(expected_author, item["article-author"])
                self.assertEqual(expected_headline, item["article-headline"])
                self.assertEqual(expected_org, item["article-org"])
                self.assertEqual(expected_parties, item["article-parties"])
                self.assertEqual(expected_party_sentiments, item["article-party-sentiments"])
                self.assertEqual(expected_pub_date, item["article-pub-date"])
                self.assertEqual(new_s3_url, item["article-text"])
                self.assertEqual(expected_topic_sentiments, item["article-topic-sentiments"])
                self.assertEqual(expected_topics, item["article-topics"])
                self.assertEqual(expected_headline_party_sentiments, item["headline-party-sentiments"])
                self.assertEqual(expected_headline_topic_sentiments, item["headline-topic-sentiments"])
                self.assertEqual(expected_likely_party, item["most-likely-party"])
                self.assertEqual(expected_top_words, item["top-words"])


            self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

            # Cleanup

            # Delete DynamoDB item
            try:
                self.articleUploader.table.delete_item(
                    Key={
                        'article-url': self.article_url
                    }
                )
            except:
                self.assertTrue(False)
            else:
                # Check item has been deleted
                response = self.articleUploader.table.get_item(
                    Key={
                        'article-url': self.article_url
                    }
                )

                try:
                    item = response['Item']
                except:
                    pass
                else:
                    self.assertTrue(False)

    def isLogEmpty(self):
        is_empty = False
        try:
            is_empty = os.stat(self.log_path).st_size == 0
        except:
            is_empty = not(path.exists(self.log_path))
        
        return is_empty

    def tearDown(self):

        # Delete any temp files created
        try:
            os.remove(self.articleUploader.tempUploadPath)
        except:
            pass

        try:
            os.remove("testing/unit/test_data/www.testurl.co.ukFYPSLASHFYPdummyFYPSLASHFYPdummy2.txt")
        except:
            pass

        # Delete any logs created
        try:
            os.remove(self.log_path)
        except:
            pass
