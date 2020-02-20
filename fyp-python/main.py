import os
import boto3

# News scraping classes
from news_scraper.NewsScraper import NewsScraper
from news_scraper.ArticleTrimmer import ArticleTrimmer
from news_scraper.ArticleUploader import ArticleUploader

# Text analysis classes
from sentiment_processor.ArticlePreProcessor import ArticlePreProcessor
from sentiment_processor.ArticleAnalyser import ArticleAnalyser
from sentiment_processor.AnalysisUploader import AnalysisUploader

# Helper classes
from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

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

# Write to log saying program has started
logger = Logger()
log_line = "\n\nScript started at: "
logger.writeToLog(log_line, True)

# Initialise text pre-processing class
preprocessor = TextPreprocessor(logger)

# Get articles
newsScraper = NewsScraper(dynamodb, logger) #TODO investigate why less daily mail and telegraph articles
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer(logger)
database_entry = articleTrimmer.trimArticle(articles)

# Upload articles and relevant metadata to S3 and DynamoDB
articleUploader = ArticleUploader(s3, bucket_name, dynamodb, logger)
articleUploader.uploadArticles(database_entry)

# Write to log file, stating scraping aspect's completion
log_line = "Article scraping ran to completion - "
logger.writeToLog(log_line, True)

# Begin processing of all articles text
for article_url, article_metadata in database_entry.items():

    # Retrieve necessary article data
    article_text = article_metadata[0]
    article_headline = article_metadata[1]

    # Get required information from the article
    articleAnalyser = ArticleAnalyser(logger, article_text, article_headline, preprocessor)
    articleAnalyser.analyseTopicsSentiment()
    #articleAnalyser.analyseEntitySentiment() # TODO add back this call once func implemented
    mostSimilarManifesto = articleAnalyser.analyseManifestoSimilarity()

    # Write analysis information to DynamoDB
    analysisUploader = AnalysisUploader(logger)
    analysisUploader.pushAnalysis()

# Write to log file, stating program's completion
log_line = "Script ran to completion - "
logger.writeToLog(log_line, True)
