'''
DynamoDB table:
    Party (i.e. Labour, Conservatives)
    Top words (Pairs of word and word frequency - for word map)
    Topic-sentiment matrix (Pairs of topic and sentiment score)
'''

import os
import boto3
import re
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
logger = Logger()
preprocessor = TextPreprocessor(logger)

topic_model_path = "assets/model-final/topic_model.pkl"
topic_vectorizer_path = "assets/model-final/topic_vectorizer.pkl"

party_model_path = "assets/model-final/party_model.pkl"
party_vectorizer_path = "assets/model-final/party_vectorizer.pkl"

try:
    topic_model = cPickle.load(open(topic_model_path, 'rb'))
except:
    print("Model: " + topic_model_path + " not found")
    exit(0)

try:
    topic_vectorizer = cPickle.load(open(topic_vectorizer_path, "rb"))
except:
    print("Vectorizer: " + topic_vectorizer_path + " not found")
    exit(0)

try:
    party_model = cPickle.load(open(party_model_path, 'rb'))
except:
    print("Model: " + party_model_path + " not found")
    exit(0)

try:
    party_vectorizer = cPickle.load(open(party_vectorizer_path, "rb"))
except:
    print("Vectorizer: " + party_vectorizer_path + " not found")
    exit(0)

manifesto_party_sentiments = {
    PoliticalPartyHelper.PoliticalParty.brexitParty: "Conservatives = 0.8, Green = -1, Labour = -1, Liberal Democrats = -1, Plaid Cymru = -1, SNP = -1, UKIP = 0.8",
    PoliticalPartyHelper.PoliticalParty.conservative: "Brexit Party = 0.25., Green = -1, Labour = -1, Liberal Democrats = -1 Plaid Cymru = -1, SNP = -1, UKIP = -0.8",
    PoliticalPartyHelper.PoliticalParty.labour: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Liberal Democrats = -0.75, Plaid Cymru = -0.75, SNP = -0.75, UKIP = -1",
    PoliticalPartyHelper.PoliticalParty.libDem: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Plaid Cymru = -0.75, SNP = -0.75, UKIP = -1",
    PoliticalPartyHelper.PoliticalParty.green: "Brexit Party = -1, Conservatives = -1, Labour = -0.75, Liberal Democrats = -0.75, Plaid Cymru = -0.75, SNP = -0.75, UKIP = -1",
    PoliticalPartyHelper.PoliticalParty.plaidCymru: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Liberal Democrats = -0.75, SNP = 0, UKIP = -1",
    PoliticalPartyHelper.PoliticalParty.SNP: "Brexit Party = -1, Conservatives = -1, Green = -0.75, Labour = -0.75, Liberal Democrats = -0.75, Plaid Cymru = 0, UKIP = -1",
    PoliticalPartyHelper.PoliticalParty.UKIP: "Brexit Party = 0.8, Conservatives = 0.75, Green = -1, Labour = -1, Liberal Democrats = -1, Plaid Cymru = -1, SNP = -1"
}

base_manifesto_path = "manifesto_scraper/manifestos/"
base_top_words_path = "manifesto_scraper/unibimix/"

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
    
    # Split manifesto into paragraphs
    manifesto_file_path = base_manifesto_path + manifesto_file

    with open(manifesto_file_path , "r", encoding="unicode_escape") as manifesto_file:
        manifesto_text = manifesto_file.read()
        manifesto_file.close()

    # Create dictionary, key: topic index, value: sentiment scores
    topic_sentiment_scores = {}

    # Then, get sentiment scores for mentioned topics and parties by the manifesto
    articleAnalyser = ArticleAnalyser(logger, manifesto_text, manifesto_file_path, "", preprocessor)

    analysed_topics = articleAnalyser.analyseArticleSentiment(True) # Get topic sentiment
    manifesto_topic_sentiment_matrix = analysed_topics[1]

    # analysed_parties = articleAnalyser.analyseArticleSentiment(False) # Get party sentiment
    # manifesto_party_sentiment_matrix = analysed_parties[1]

    # Store results in string-encoded matrix
    manifesto_topic_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in manifesto_topic_sentiment_matrix.items() if topic_num != 0])
    manifesto_topic_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in manifesto_topic_sentiment_matrix.items()])

    manifesto_party_sentiment_matrix = manifesto_party_sentiments[political_party]
    # Remove the current party from party-sentiment matrix (don't care about a party's opinion about itself!)
    # manifesto_party_sentiment_matrix = dict([(PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[party_num]], party_sentiment) for party_num,party_sentiment in manifesto_party_sentiment_matrix.items() if party_num != 0 and PoliticalPartyHelper.partyNumToEnum[party_num] != current_political_party])
    # manifesto_party_sentiment_matrix = ", ".join([party + " = " + str(score) for party, score in manifesto_party_sentiment_matrix.items()])

    response = parties_table.update_item( # update database entry with new text and metadata
        Key={
            'party-name': current_political_party
        },
        ExpressionAttributeNames = { # necessary as "-" in column names cause issues
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