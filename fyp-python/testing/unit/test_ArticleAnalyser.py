import os
from os import path
import unittest
import numpy as np

from sentiment_processor.ArticleAnalyser import ArticleAnalyser
from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor
from helper_classes.Enums import PoliticalPartyHelper

class TestArticleAnalyser(unittest.TestCase):

    def setUp(self):

        # Initialise log file, and logger
        self.log_path = "temp_files/testLog.txt"
        logger = Logger(self.log_path)
        
        # Initialise preprocessor
        preprocessor = TextPreprocessor(logger)

        # Initialise test data variables
        self.article_filename = "testing/unit/test_data/article_analysis_test.txt"

        with open(self.article_filename, "r", encoding="unicode_escape") as article_file:
            article_text = article_file.read()
            article_file.close()

        headline = "SNP manifesto 2019: 12 key policies explained"

        self.articleAnalyser = ArticleAnalyser(logger, article_text, self.article_filename, headline, preprocessor)

    def test_analyseArticleSentiment(self):
        # Arrange

        # Act
        returned = self.articleAnalyser.analyseArticleSentiment(True)
        likely_topics = returned[0]
        topic_matrix = returned[1]

        returned = self.articleAnalyser.analyseArticleSentiment(False)
        likely_parties = returned[0]
        party_matrix = returned[1]

        # Act again (for consistency test)
        self.articleAnalyser.entity_tracker = {}
        returned = self.articleAnalyser.analyseArticleSentiment(True)
        rerun_likely_topics = returned[0]
        rerun_topic_matrix = returned[1]

        returned = self.articleAnalyser.analyseArticleSentiment(False)
        rerun_likely_parties = returned[0]
        rerun_party_matrix = returned[1]

        # Assert
        self.assertTrue(likely_topics.tolist()) # True = Non-empty
        self.assertTrue(likely_parties.tolist()) # True = Non-empty

        self.assertTrue(topic_matrix) # True = Non-empty
        self.assertTrue(party_matrix) # True = Non-empty

        self.assertEqual(likely_topics.tolist(), rerun_likely_topics.tolist())
        self.assertEqual(likely_parties.tolist(), rerun_likely_parties.tolist())

        self.assertDictEqual(topic_matrix, rerun_topic_matrix)
        self.assertDictEqual(party_matrix, rerun_party_matrix)

        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions
        

    def test_analyseManifestoSimilarity(self): 
        # Arrange
        expected_most_similar_party = PoliticalPartyHelper.PoliticalParty.SNP

        # Act
        most_similar_party = self.articleAnalyser.analyseManifestoSimilarity()

        # Assert
        self.assertIsNotNone(most_similar_party)
        self.assertEqual(expected_most_similar_party, most_similar_party)

        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def test_analyseHeadlineSentiment(self):
        # Arrange

        # Act
        topic_matrix = self.articleAnalyser.analyseHeadlineSentiment(True)
        party_matrix = self.articleAnalyser.analyseHeadlineSentiment(False)

        # Act again (for consistency test)
        self.articleAnalyser.entity_tracker = {}
        rerun_topic_matrix = self.articleAnalyser.analyseHeadlineSentiment(True)
        rerun_party_matrix = self.articleAnalyser.analyseHeadlineSentiment(False)

        # Assert
        self.assertTrue(topic_matrix) # True = Non-empty
        self.assertTrue(party_matrix) # True = Non-empty

        self.assertDictEqual(topic_matrix, rerun_topic_matrix)
        self.assertDictEqual(party_matrix, rerun_party_matrix)

        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def test_getTopWords(self):
        # Arrange

        # Act
        top_words = self.articleAnalyser.getTopWords()
        top_words_2 = self.articleAnalyser.getTopWords()

        # Assert
        self.assertTrue(top_words.tolist())
        self.assertEqual(20, len(top_words))
        self.assertTrue(self.isLogEmpty()) # Empty log = No exceptions

    def test_getVectorised(self):

        # Arrange
        topic_vectorizer = self.articleAnalyser.topic_vectorizer
        party_vectorizer = self.articleAnalyser.party_vectorizer

        # Act
        text_vectorized_topic = self.articleAnalyser.getVectorised(self.article_filename, topic_vectorizer)
        text_vectorized_party = self.articleAnalyser.getVectorised(self.article_filename, party_vectorizer)
   
        # Assert
        self.assertIsNotNone(text_vectorized_topic)
        self.assertIsNotNone(text_vectorized_party)
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
