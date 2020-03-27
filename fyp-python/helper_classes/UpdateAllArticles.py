import os
import re
import boto3
import requests
import urllib3
import certifi
from bs4 import BeautifulSoup
from datetime import datetime

from sentiment_processor.ArticleAnalyser import ArticleAnalyser

from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor
from helper_classes.Enums import PoliticalPartyHelper, TopicsHelper

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

table = dynamodb.Table('Articles-Table')

# Initialise other variables
logger = Logger()  
preprocessor = TextPreprocessor(logger)

news_org_pub_date = {
    "BBC": ["div", "class", "date date--v2"], # Get first one, and get text
    "DAILY MAIL": ["meta", "property", "article:published_time"], # get content
    "TELEGRAPH": ["meta", "itemprop", "datePublished"], # Get first one, and get ["content"],
    "GUARDIAN": ["meta", "property", "article:published_time"], # Get content
    "INDEPENDENT": ["meta", "property", "article:published_time"], # get content
    "MIRROR": ["meta", "property","article:published_time"] # get content
}

# Write to log saying program has started
logger = Logger()
log_line = "\n\nScript started at: "
logger.writeToLog(log_line, True)

still_items_left = True
first_scan = True

last_evaluated_key = ""

while(still_items_left):
    skipped = 0

    if (first_scan):
        results = table.scan()
        first_scan = False
    else:
        results = table.scan(ExclusiveStartKey=last_evaluated_key) # due to DynamoDB's pagination of results
    try:
        last_evaluated_key = results["LastEvaluatedKey"]
    except:
        still_items_left = False

    print(len(results["Items"]))
    for item in results["Items"]:
        try:
            x = item['article-parties']
        except:
            article_url = item['article-url']
            article_org = item['article-org']
            article_headline = item['article-headline']

            article_pub_date = ""

            skip = False

            # Get article publish date
            try:
                response = urllib3.PoolManager(
                    cert_reqs='CERT_REQUIRED',
                    ca_certs=certifi.where()
                ).request('GET', article_url)
            except Exception as e:
                try:
                    response = requests.get(article_url) # try using requests
                except:
                    skip = True
                    log_line = "Link failed - check url validity: " + article_url
                    log_line += "\nFailed with following exception:\n"
                    log_line += str(e)
                    logger.writeToLog(log_line, False)
            try:
                soup = BeautifulSoup(response.data, 'html.parser')
            except:
                try:
                    soup = BeautifulSoup(response.text, 'html.parser') # requests uses 'text' instead of 'data'
                except:
                    skip = True
                    log_line = "Soup-ing failed - is URL xml: " + article_url
                    log_line += "\nFailed with the folowing exception:\n"
                    log_line += e
                    logger.writeToLog(log_line, False)

            if (not skip):
                pub_dates = soup.find_all(news_org_pub_date[article_org][0], {news_org_pub_date[article_org][1]:news_org_pub_date[article_org][2]})

                for pub_date in pub_dates:
                
                    if (article_org == "BBC"):
                        article_pub_date = pub_date.getText()
                        break
                    else:
                        article_pub_date = pub_date["content"]
                        break
                
                if (article_org != "BBC"):
                    try:
                        article_pub_date = datetime.strptime(article_pub_date.split("T")[0], "%Y-%m-%d")
                    except Exception as e:
                        print(e)
                        print(article_pub_date)
                        print(article_url + " failed")
                    else:
                        article_pub_date = datetime.strftime(article_pub_date, "%d %B %Y")

            # Get article text
            s3_object_url = item['article-text']
            # Download article text and save as .txt
            s3_object_filename = (s3_object_url.split("amazonaws.com/"))[1]
            # Get rid of anything after .txt
            trimmed = s3_object_filename.split(".txt")[0] + ".txt"
            trimmed = re.sub(r'[/\\:*?"<>|]', '', trimmed)
            local_filename = 'temp_files/' + trimmed
            s3.Bucket(bucket_name).download_file(s3_object_filename, local_filename)
            
            with open(local_filename, "r", encoding="unicode_escape") as article_text_file:
                article_text = article_text_file.read()
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

            # Encode it for database
            likely_topics = ", ".join([TopicsHelper.topicIndexToTopic[likely_topic] for likely_topic in likely_topics if likely_topic != 0])

            likely_parties = ", ".join([PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[likely_party]] for likely_party in likely_parties if likely_party != 0])

            article_topic_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in article_topic_sentiment_matrix.items() if topic_num != 0])
            article_topic_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in article_topic_sentiment_matrix.items()])

            article_party_sentiment_matrix = dict([(PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[party_num]], party_sentiment) for party_num,party_sentiment in article_party_sentiment_matrix.items() if party_num != 0])
            article_party_sentiment_matrix = ", ".join([party + " = " + str(score) for party, score in article_party_sentiment_matrix.items()])

            most_similar_party = PoliticalPartyHelper.enumToPoliticalPartyString[most_similar_party]

            headline_topics_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in headline_topics_sentiment_matrix.items() if topic_num != 0])
            headline_topics_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in headline_topics_sentiment_matrix.items()])

            headline_parties_sentiment_matrix = dict([(PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[party_num]], party_sentiment) for party_num,party_sentiment in headline_parties_sentiment_matrix.items() if party_num != 0])
            headline_parties_sentiment_matrix = ", ".join([party + " = " + str(score) for party, score in headline_parties_sentiment_matrix.items()])

            top_words = ", ".join([word + " = " + str(score) for word,score in top_words.items()])

            if (article_pub_date == ""):
                article_pub_date = "NO INFO"
            if (likely_topics == ""):
                likely_topics = "NO INFO"
            if (likely_parties == ""):
                likely_parties = "NO INFO"
            if (article_topic_sentiment_matrix == ""):
                article_topic_sentiment_matrix = "NO INFO"
            if (article_party_sentiment_matrix == ""):
                article_party_sentiment_matrix = "NO INFO"
            if (most_similar_party == ""):
                most_similar_party = "NO INFO"
            if (headline_topics_sentiment_matrix == ""):
                headline_topics_sentiment_matrix = "NO INFO"
            if (headline_parties_sentiment_matrix == ""):
                headline_parties_sentiment_matrix = "NO INFO"
            if (top_words == ""):
                top_words = "NO INFO"

            response = table.update_item( # update database entry with new text and metadata
                Key={
                    'article-url': article_url
                },
                ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                    "#ap":"article-pub-date",
                    "#atp":"article-topics",
                    "#apr":"article-parties",
                    "#ats":"article-topic-sentiments",
                    "#aps":"article-party-sentiments",
                    "#mlp":"most-likely-party",
                    "#hts":"headline-topic-sentiments",
                    "#hps":"headline-party-sentiments",
                    "#tw":"top-words"
                },
                UpdateExpression="SET #ap=:p, #atp=:t, #apr=:r, #ats=:s, #aps=:q, #mlp=:m, #hts=:h, #hps=:z, #tw=:w",
                ExpressionAttributeValues={
                    ':p': article_pub_date,
                    ':t': likely_topics,
                    ':r': likely_parties,
                    ':s': article_topic_sentiment_matrix,
                    ':q': article_party_sentiment_matrix,
                    ':m': most_similar_party,
                    ':h': headline_topics_sentiment_matrix,
                    ':z': headline_parties_sentiment_matrix,
                    ':w': top_words,            
                },
                ReturnValues="UPDATED_NEW"
            )

            os.remove(local_filename)
        else:
            skipped += 1

    print("skipped: " + str(skipped))

        
    


