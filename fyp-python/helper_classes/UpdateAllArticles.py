import os
import re
import csv
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
preprocessor = TextPreprocessor()

# Write to log saying program has started
logger = Logger()
log_line = "\n\nScript started at: "
logger.writeToLog(log_line, True)

still_items_left = True
first_scan = True

last_evaluated_key = ""

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

# UNCOMMENT FOR FULL RUN - RUN different instances for faster upload
# Keys
#key = {}
#key = {'article-url': 'https://www.mirror.co.uk/news/politics/voice-mirror-welcome-boris-johnsons-21459185'}
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8143251/Fit-healthy-mother-39-face-coronavirus-epidemic-released-hospital.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}
#key = {'article-url': 'https://www.independent.co.uk/news/uk/politics/keir-starmer-labour-leadership-race-unison-trade-union-corbyn-long-bailey-a9275366.html'}
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8020153/MEPs-warn-Britain-EU-fishermen-rights-fish-British-waters.html?ns_mchannel=rss&ns_campaign=1490&ito=1490'}
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8142633/Thieves-raid-kitchens-fridges-food-destined-locals-left-isolated-coronavirus.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}      
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8154805/Fury-Sadiq-Khan-grows-workers-forced-packed-Tubes-3rd-day-coronavirus-lockdown.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}    
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8186835/Wealthy-NYC-businesses-board-stores-defend-against-civil-unrest-virus-decimates-NYPD.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-8154891/Coronavirus-tracker-claims-6-6MILLION-people-UK-it.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}
#key = {'article-url': 'https://www.dailymail.co.uk/news/article-7747291/Jeremy-Corbyn-criticised-video-supporting-minority-groups-excludes-Jewish-community.html?ns_mchannel=rss&ito=1490&ns_campaign=1490'}

local_filename = "temp_files/tempArticleFile1.txt"
#local_filename = "temp_files/tempArticleFile2.txt"
#local_filename = "temp_files/tempArticleFile3.txt"
#local_filename = "temp_files/tempArticleFile4.txt"
#local_filename = "temp_files/tempArticleFile5.txt"
#local_filename = "temp_files/tempArticleFile6.txt"
#local_filename = "temp_files/tempArticleFile7.txt"
#local_filename = "temp_files/tempArticleFile8.txt"
#local_filename = "temp_files/tempArticleFile9.txt"
#local_filename = "temp_files/tempArticleFile10.txt"

# if (key == {}):
#     results = table.scan()
# else:
#     results = table.scan(ExclusiveStartKey=key) # due to DynamoDB's pagination of results

# total = len(results["Items"])
# counter = 0

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

    total = len(results["Items"])
    counter = 0

    for item in results["Items"]:
        try:
            x = item["updated"]
        except:
            counter +=1
            remaining = str(counter) + "/" + str(total)
            print(remaining, end="\r")

            article_url = item['article-url']
            article_org = item['article-org']
            article_headline = item['article-headline']

            # Get article text
            s3_object_url = item['article-text']
            # Download article text and save as .txt
            s3_object_filename = (s3_object_url.split("amazonaws.com/"))[1]
            # Get rid of anything after .txt
            trimmed = s3_object_filename.split(".txt")[0] + ".txt"
            trimmed = re.sub(r'[/\\:*?"<>|]', '', trimmed)
            s3.Bucket(bucket_name).download_file(s3_object_filename, local_filename)
            
            with open(local_filename, "r", encoding="unicode_escape") as article_text_file:
                article_text = article_text_file.read()
                article_text_file.close()

            # Get required information from the article
            articleAnalyser = ArticleAnalyser(logger, article_text, article_headline, preprocessor, mps, manifesto_texts)

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

            try:
                response = table.update_item( # update database entry with new text and metadata
                    Key={
                        'article-url': article_url
                    },
                    ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                        "#atp":"article-topics",
                        "#apr":"article-parties",
                        "#ats":"article-topic-sentiments",
                        "#aps":"article-party-sentiments",
                        "#mlp":"most-likely-party",
                        "#hts":"headline-topic-sentiments",
                        "#hps":"headline-party-sentiments",
                        "#tw":"top-words",
                        "#do":"updated"
                    },
                    UpdateExpression="SET #atp=:t, #apr=:r, #ats=:s, #aps=:q, #mlp=:m, #hts=:h, #hps=:z, #tw=:w, #do=:d",
                    ExpressionAttributeValues={
                        ':t': likely_topics,
                        ':r': likely_parties,
                        ':s': article_topic_sentiment_matrix,
                        ':q': article_party_sentiment_matrix,
                        ':m': most_similar_party,
                        ':h': headline_topics_sentiment_matrix,
                        ':z': headline_parties_sentiment_matrix,
                        ':w': top_words,  
                        ':d': "UPDATED"     
                    },
                    ReturnValues="UPDATED_NEW"
                )
            except:
                logger.writeToLog("Failed to upload to DB - retrying...", False)
                try:
                    response = table.update_item( # update database entry with new text and metadata
                        Key={
                            'article-url': article_url
                        },
                        ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                            "#atp":"article-topics",
                            "#apr":"article-parties",
                            "#ats":"article-topic-sentiments",
                            "#aps":"article-party-sentiments",
                            "#mlp":"most-likely-party",
                            "#hts":"headline-topic-sentiments",
                            "#hps":"headline-party-sentiments",
                            "#tw":"top-words",
                            "#do":"updated"
                        },
                        UpdateExpression="SET #atp=:t, #apr=:r, #ats=:s, #aps=:q, #mlp=:m, #hts=:h, #hps=:z, #tw=:w, #do=:d",
                        ExpressionAttributeValues={
                            ':t': likely_topics,
                            ':r': likely_parties,
                            ':s': article_topic_sentiment_matrix,
                            ':q': article_party_sentiment_matrix,
                            ':m': most_similar_party,
                            ':h': headline_topics_sentiment_matrix,
                            ':z': headline_parties_sentiment_matrix,
                            ':w': top_words,  
                            ':d': "UPDATED"     
                        },
                        ReturnValues="UPDATED_NEW"
                    )
                except:
                    logger.writeToLog("Failed again - skipping...", False)
                    logger.writeToLog("Failed URL - " + article_url, False)
        else:
            continue
        

os.remove(local_filename)

        
    



