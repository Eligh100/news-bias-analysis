'''
DynamoDB table:
    Party (i.e. Labour, Conservatives)
    Top words (Pairs of word and word frequency - for word map)
    Topic-sentiment matrix (Pairs of topic and sentiment score)
'''

import os
import boto3
import re
import csv
import numpy as np
import pandas as pd
import tkinter
import matplotlib
import matplotlib.pyplot as plt
import scipy.sparse as ss
import _pickle as cPickle
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.tokenize import sent_tokenize
from corextopic import corextopic as ct
from corextopic import vis_topic as vt

from helper_classes.Enums import PoliticalPartyHelper
from helper_classes.Enums import TopicsHelper
from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

from sentiment_processor.ArticleAnalyser import ArticleAnalyser

# Establish AWS-related variables
ACCESS_KEY_ID = "AKIASRO4ILWKGIB27HGU"
SECRET_ACCESS_KEY = "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"

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id = ACCESS_KEY_ID,
    aws_secret_access_key = SECRET_ACCESS_KEY
    )

parties_table = dynamodb.Table('Parties-Table')

# Other preliminary variables
logger = Logger(log_path="manifesto_scraper/manifestoInfoUploadLog.txt")
preprocessor = TextPreprocessor()

manifesto_party_sentiments = {
    PoliticalPartyHelper.PoliticalParty.brexitParty: "Conservatives = 0.8, Green = -1, Labour = -1, Liberal Democrats = -1, Plaid Cymru = -1, SNP = -1",
    PoliticalPartyHelper.PoliticalParty.conservative: "Brexit Party = 0.25., Green = -1, Labour = -1, Liberal Democrats = -1 Plaid Cymru = -1, SNP = -1",
    PoliticalPartyHelper.PoliticalParty.labour: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Liberal Democrats = -0.75, Plaid Cymru = -0.75, SNP = -0.75",
    PoliticalPartyHelper.PoliticalParty.libDem: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Plaid Cymru = -0.75, SNP = -0.75",
    PoliticalPartyHelper.PoliticalParty.green: "Brexit Party = -1, Conservatives = -1, Labour = -0.75, Liberal Democrats = -0.75, Plaid Cymru = -0.75, SNP = -0.75",
    PoliticalPartyHelper.PoliticalParty.plaidCymru: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Liberal Democrats = -0.75, SNP = 0",
    PoliticalPartyHelper.PoliticalParty.SNP: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Liberal Democrats = -0.75, Plaid Cymru = 0",
}

base_manifesto_path = "manifesto_scraper/manifestos/"
base_top_words_path = "manifesto_scraper/bigrams/"

# Open MPs CSV and store results in dict
mps = {}
try:
    with open("assets/political-people.csv") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            mps[row[0]] = row[1]
        csvfile.close()
except Exception as e:
    print("Failed to open MPs CSV")
    exit(0)

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
    print("Failed to store manifesto texts")
    exit(0)

for top_words_file, manifesto_file, political_party in zip(os.listdir(base_top_words_path), os.listdir(base_manifesto_path), PoliticalPartyHelper.PoliticalParty):
    
    # Get political party name
    current_political_party = PoliticalPartyHelper.enumToPoliticalPartyString[political_party]
    
    current_top_words_path = base_top_words_path + top_words_file

    lines = []
    with open(current_top_words_path, "r", encoding="utf-8") as current_top_words_file:
        lines = current_top_words_file.readlines()
        current_top_words_file.close()
    
    # Get top words
    top_words = ", ".join(lines)
    top_words = top_words.replace("\n", "")
    
    # Get manifestos opinions on topics
    manifesto_file_path = base_manifesto_path + manifesto_file

    with open(manifesto_file_path , "r", encoding="unicode_escape") as manifesto_file:
        manifesto_text = manifesto_file.read()
        manifesto_file.close()

    # Then, get sentiment scores for mentioned topics and parties by the manifesto
    articleAnalyser = ArticleAnalyser(logger, manifesto_text, manifesto_file_path, "", preprocessor, mps, manifesto_texts)

    analysed_topics = articleAnalyser.analyseArticleSentiment(True) # Get topic sentiment
    manifesto_topic_sentiment_matrix = analysed_topics[1]

    # Store results in string-encoded matrix
    manifesto_topic_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in manifesto_topic_sentiment_matrix.items() if topic_num != 0])
    manifesto_topic_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in manifesto_topic_sentiment_matrix.items()])

    manifesto_party_sentiment_matrix = manifesto_party_sentiments[political_party]

    response = parties_table.update_item( # Update database entry with new text and metadata
        Key={
            'party-name': current_political_party
        },
        ExpressionAttributeNames = { # Necessary as "-" in column names cause issues
            "#tw":"top_words",
            "#tsm":"topics_sentiment_matrix",
            "#psm":"parties_sentiment_matrix"
        },
        UpdateExpression="SET #tw=:w, #tsm=:t, #psm=:p",
        ExpressionAttributeValues={
            ':w': top_words,
            ':t': manifesto_topic_sentiment_matrix,
            ':p': manifesto_party_sentiment_matrix      
        },
        ReturnValues="UPDATED_NEW"
    )