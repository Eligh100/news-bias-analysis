import os
import boto3
import csv

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
preprocessor = TextPreprocessor()

# Get articles
newsScraper = NewsScraper(dynamodb, logger)
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer(logger)
database_entry = articleTrimmer.trimArticle(articles)

# Write to log file, stating scraping aspect's completion
log_line = "Article scraping ran to completion - "
logger.writeToLog(log_line, True)

table = dynamodb.Table('Articles-Table')

# Open MPs CSV and store results in dict
mps = {}
try:
    with open("assets/political-people.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            mps[row[0]] = row[1]
        csvfile.close()
except Exception as e:
    log_line = "Reading of MPs CSV file at: assets/political-people.csv failed"
    log_line += "\nFailed with the folowing exception:\n"
    log_line += str(e)
    logger.writeToLog(log_line, False)

# Get manifesto texts
manifesto_texts = []
try:
    for manifestoProcessed in os.listdir('manifesto_scraper/manifestosProcessed'):
        manifestoFilePath = "manifesto_scraper/manifestosProcessed/" + manifestoProcessed
        with open(manifestoFilePath , "r", encoding="utf-8") as manifestoTextFile:
            manifestoText = manifestoTextFile.read()
            manifesto_texts.append(manifestoText)
            manifestoTextFile.close()
except Exception as e:
    log_line = "Unable to locate manifestos"
    log_line += "\nFailed with the folowing exception:\n"
    log_line += str(e)
    log_line += "\nScript exited prematurely - "
    logger.writeToLog(log_line, True)
    exit(0)

# Begin processing of all articles text
for article_url, article_metadata in database_entry.items():

    # Retrieve necessary article data
    article_text = article_metadata[0]
    article_headline = article_metadata[1]

    # Get required information from the article
    articleAnalyser = ArticleAnalyser(logger, article_text, article_headline, preprocessor, mps, manifesto_texts)

    # Extract topic opinions from the article's body
    analysed_topics = articleAnalyser.analyseArticleSentiment(True) # Get topic sentiment
    likely_topics = analysed_topics[0]
    article_topic_sentiment_matrix = analysed_topics[1]

    # Extract party opinions from the article's body
    analysed_parties = articleAnalyser.analyseArticleSentiment(False) # Get party sentiment
    likely_parties = analysed_parties[0]
    article_party_sentiment_matrix = analysed_parties[1]

    # Extract topic and party opinions from the headline
    headline_topics_sentiment_matrix = articleAnalyser.analyseHeadlineSentiment(True)
    headline_parties_sentiment_matrix = articleAnalyser.analyseHeadlineSentiment(False)

    # See which manifesto the article shares language with
    most_similar_party = articleAnalyser.analyseManifestoSimilarity()

    # Get the top 20 words from the article
    top_words = articleAnalyser.getTopWords()

    # Reset entity tracker for next article
    articleAnalyser.entity_tracker = {}

    # Write analysis information to DynamoDB and upload article text
    articleUploader = ArticleUploader(s3, bucket_name, table, logger, likely_topics, likely_parties, article_topic_sentiment_matrix, article_party_sentiment_matrix, most_similar_party, headline_topics_sentiment_matrix, headline_parties_sentiment_matrix, top_words)
    articleUploader.uploadArticles(article_url, database_entry[article_url])

# Remove temp file for uploading files
try:
    os.remove(articleUploader.tempUploadPath)
except Exception as e:
    log_line = "Failed to remove temp upload text file at: " + articleUploader.tempUploadPath
    log_line += "\nFailed with the folowing exception:\n"
    log_line += str(e)
    logger.writeToLog(log_line, False)

# Write to log file, stating program's completion
log_line = "Script ran to completion - "
logger.writeToLog(log_line, True)
