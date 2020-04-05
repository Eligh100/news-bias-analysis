import os
import boto3

# News scraping classes
from news_scraper.NewsScraper import NewsScraper
from news_scraper.ArticleTrimmer import ArticleTrimmer

# Text analysis classes
from helper_classes.TextPreprocessor import TextPreprocessor
from sentiment_processor.ArticleAnalyser import ArticleAnalyser
from sentiment_processor.ArticleUploader import ArticleUploader

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
newsScraper = NewsScraper(dynamodb, logger)
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer(logger)
database_entry = articleTrimmer.trimArticle(articles)

# Write to log file, stating scraping aspect's completion
log_line = "Article scraping ran to completion - "
logger.writeToLog(log_line, True)

local_filename = 'temp_files/tempArticleFile.txt'
table = dynamodb.Table('Articles-Table')

# Begin processing of all articles text
for article_url, article_metadata in database_entry.items():

    # Retrieve necessary article data
    article_text = article_metadata[0]
    article_headline = article_metadata[1]

    # Write article text to temporary file for processing
    with open(local_filename, "w", encoding="unicode_escape") as article_text_file:
        article_text_file.write(article_text)
        article_text_file.close()

    # Get required information from the article
    articleAnalyser = ArticleAnalyser(logger, article_text, local_filename, article_headline, preprocessor)

    analysed_topics = articleAnalyser.analyseArticleSentiment(True) # Get topic sentiment
    likely_topics = analysed_topics[0]
    article_topic_sentiment_matrix = analysed_topics[1]

    analysed_parties = articleAnalyser.analyseArticleSentiment(False) # Get party sentiment
    likely_parties = analysed_parties[0]
    article_party_sentiment_matrix = analysed_parties[1]

    most_similar_party = articleAnalyser.analyseManifestoSimilarity()

    headline_topics_sentiment_matrix = articleAnalyser.analyseHeadlineSentiment(True)
    headline_parties_sentiment_matrix = articleAnalyser.analyseHeadlineSentiment(False)

    top_words = articleAnalyser.getTopWords()

    # Write analysis information to DynamoDB and upload article text
    articleUploader = ArticleUploader(s3, bucket_name, table, logger, likely_topics, likely_parties, article_topic_sentiment_matrix, article_party_sentiment_matrix, most_similar_party, headline_topics_sentiment_matrix, headline_parties_sentiment_matrix, top_words)
    articleUploader.uploadArticles(article_url, database_entry[article_url])

try:
    os.remove(local_filename)
except:
    log_line = "Failed to remove temp article text file"
    logger.writeToLog(log_line, False)

# Write to log file, stating program's completion
log_line = "Script ran to completion - "
logger.writeToLog(log_line, True)
