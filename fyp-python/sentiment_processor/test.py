from ArticleAnalyser import ArticleAnalyser
from AnalysisUploader import AnalysisUploader
import smart_open

from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

testFile = open("assets/test_articles/testDoc.txt", "r", encoding="utf-8")
article_text = testFile.read()
testFile.close()

logger = Logger()  
preprocessor = TextPreprocessor(logger)

# Get required information from the article
articleAnalyser = ArticleAnalyser(logger, article_text, "Immigration: No visas for low-skilled workers, government says", preprocessor)
articleAnalyser.analyseTopicsSentiment()

