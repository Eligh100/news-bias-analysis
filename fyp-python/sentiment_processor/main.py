from ArticlePreProcessor import ArticlePreProcessor
from ArticleAnalyser import ArticleAnalyser
import boto3
import smart_open

'''
THIS IS TO BE RAN TWICE A DAY (AFTER SCRAPING)
However, one big run will occur, for all articles currently saved and stored
'''

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

# mock s3 article
s3_article_url = "https://articles-text.s3.eu-west-2.amazonaws.com/www.independent.co.ukFYPSLASHFYPnewsFYPSLASHFYPukFYPSLASHFYPpoliticsFYPSLASHFYPboris-johnson-brexit-bill-pass-parliament-eu-latest-today-a9297601.html.txt"

article_text = ""
for line in smart_open.open(s3_article_url):
    article_text += line + " "

# Do pre-processing for each one (tokinisation)
articlePreProcessor = ArticlePreProcessor()
preprocessed_text = articlePreProcessor.preprocess(article_text)

# Get required information from the article
articleAnalyser = ArticleAnalyser()
articleAnalyser.analyseLikelyTopic(preprocessed_text, article_text)
articleAnalyser.analyseEntitySentiment(articleAnalyser) # Pass unprocessed text (entity recognition may require details lost in pre-processing)

# Store this info in DynamoDB table

'''
for each article in dynamodb database (in time range - default is ALL)
retrieve article table entry
put s3 link through article preprocessor
once article is ready, obtain bias score
    topic detection
    general sentiment on those topics
    compare to political party manifesto
    find mentioned party members/mentions of party names
    combine for score
'''


'''
Reduce costs/increase speed
    Article scraped
    Pre-process article
    Run analysis on article
        Detect topics (w/ model)
        Look for named entities for each party and assign scores
    Store in DynamoDB database, w/ columns:
        S3 OBJECT URL
        NEWSPAPER
        AUTHOR(s)
        PUBLISHED DATE
        LIKELY TOPICS
        TOPICS/SENTIMENT SCORES MATRIX (i.e. list of pairs - [("Brexit","0.6"),("Climate change","0.9")])
        PARTY ENTITIES/SENTIMENT SCORES MATRIX (i.e. list of pairs - [("Labour", "0.4"),("Conservative", "-0.7")])
        WORDMAP WORDS
    
    ...

    User is on website
    


'''