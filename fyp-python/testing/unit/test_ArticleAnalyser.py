import os
from os import path
import unittest

from sentiment_processor.ArticleAnalyser import ArticleAnalyser
from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

class TestArticleAnalyser(unittest.TestCase):

    def setUp(self):

        # Initialise log file, and logger
        self.log_path = "temp_files/testLog.txt"
        logger = Logger(self.log_path)
        
        # Initialise preprocessor
        preprocessor = TextPreprocessor(logger)

        # Initialise test data variables
        article_text = ""
        article_filename = ""
        headline = ""

        self.articleAnalsyer = ArticleAnalyser(logger, article_text, article_filename, headline, preprocessor)

    def test_analyseArticleSentiment(self):
        pass

    def test_analyseManifestoSimilarity(self):
        pass

    def test_analyseHeadlineSentiment(self):
        pass

    def test_getTopWords(self):
        pass

    def test_getVectorised(self):
        pass

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
