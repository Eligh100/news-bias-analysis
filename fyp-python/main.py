from news_scraper.NewsScraper import NewsScraper
from news_scraper.ArticleTrimmer import ArticleTrimmer
from news_scraper.ArticleUploader import ArticleUploader
from helper_classes.Logger import Logger
import os
import boto3

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

# Write to log file, stating program's completion
log_line = "Script ran to completion - "
logger.writeToLog(log_line, True)

'''
Look at chronjob (Linux) for script running on servers
Basic sentiment analysis on articles?
Log errors (need to check if script has been failing, and why)
'''