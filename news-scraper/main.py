from NewsScraper import NewsScraper
from ArticleTrimmer import ArticleTrimmer
from ArticleUploader import ArticleUploader
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

# Get articles
newsScraper = NewsScraper(dynamodb) #TODO investigate why less daily mail and telegraph articles
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer()
database_entry = articleTrimmer.trimArticle(articles)

# Upload articles and relevant metadata to S3 and DynamoDB
articleUploader = ArticleUploader(s3, bucket_name, dynamodb)
articleUploader.uploadArticles(database_entry)


'''
Look at chronjob (Linux) for script running on servers
Basic sentiment analysis on articles?
Log errors (need to check if script has been failing, and why)
'''