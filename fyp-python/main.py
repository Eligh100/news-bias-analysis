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
    # Do pre-processing for each one (tokinisation)
    article_text = article_metadata[0]
    article_headline = article_metadata[1]

    articlePreProcessor = ArticlePreProcessor(logger)
    preprocessed_text = articlePreProcessor.preprocess(article_text)

    # Get required information from the article
    articleAnalyser = ArticleAnalyser(logger)
    articleAnalyser.analyseTopicsSentiment(preprocessed_text, article_text)
    articleAnalyser.analyseEntitySentiment(articleAnalyser) # Pass unprocessed text (entity recognition may require details lost in pre-processing)

    # Write analysis information to DynamoDB
    analysisUploader = AnalysisUploader(logger)
    analysisUploader.pushAnalysis()

# Write to log file, stating program's completion
log_line = "Script ran to completion - "
logger.writeToLog(log_line, True)

'''
Look at chronjob (Linux) for script running on servers
Basic sentiment analysis on articles?
Log errors (need to check if script has been failing, and why)
'''