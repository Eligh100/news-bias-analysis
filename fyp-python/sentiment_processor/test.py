from ArticleAnalyser import ArticleAnalyser
from AnalysisUploader import AnalysisUploader
import smart_open

from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

testFile = open("manifesto_scraper/testDoc.txt", "r", encoding="utf-8")
article_text = testFile.read()
testFile.close()

logger = Logger() # in real main.py, will be actual logger #TODO remove/ignore this line
preprocessor = TextPreprocessor(logger)

# Get required information from the article
articleAnalyser = ArticleAnalyser(logger, article_text, preprocessor)
articleAnalyser.analyseManifestoSimilarity()

