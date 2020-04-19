import unittest
import HtmlTestRunner

from testing.unit.test_NewsScraper import TestNewsScraper
from testing.unit.test_ArticleTrimmer import TestArticleTrimmer
from testing.unit.test_ArticleAnalyser import TestArticleAnalyser
from testing.unit.test_ArticleUploader import TestArticleUploader
from testing.unit.test_Logger import TestLogger
from testing.unit.test_TextPreprocessor import TestPreprocessor

unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output="testing/unit/report.html", combine_reports=True))