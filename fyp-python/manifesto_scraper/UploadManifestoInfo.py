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

topic_model_path = "assets/model-updated/topic_model.pkl"
vectorizer_path = "assets/model-updated/vectorizer.pkl"

try:
    topic_model = cPickle.load(open(topic_model_path, 'rb'))
except:
    print("Model: " + topic_model_path + " not found")
    exit(0)

try:
    vectorizer = cPickle.load(open(vectorizer_path, "rb"))
except:
    print("Vectorizer: " + vectorizer_path + " not found")
    exit(0)

base_manifesto_path = "manifesto_scraper/manifestos/"
base_top_words_path = "manifesto_scraper/unibimix/"

temp_file_name = "tempProcessing.txt"

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
    #top_words = [(line.split(" = ")[0], line.split(" = ")[1][:-1]) for line in lines]
    
    # Sentence tokenize each manifesto
    manifesto_file_path = base_manifesto_path + manifesto_file

    manifesto_text = ""
    with open(manifesto_file_path , "r", encoding="unicode_escape") as manifesto_file:
        manifesto_text = manifesto_file.read()
        manifesto_file.close()

    manifesto_text = preprocessor.replaceNewline(manifesto_text, ' ')
    manifesto_sentences = preprocessor.tokenizeSentences(manifesto_text)

    topic_sentiment_scores = {}

    joined_sentences = []
    counter = 1
    current_index = 0
    for sentence in manifesto_sentences:
        if (counter == 1):
            joined_sentences.append(sentence)
        elif(counter < 5):
            joined_sentences[current_index] += " " + sentence
        else:
            counter = 1
            current_index += 1
            continue
        counter += 1

    for sentence in joined_sentences:
        sentence = preprocessor.changeToLower(sentence)
        sentence = re.sub(' +', ' ', sentence)
        with open(temp_file_name, "w", encoding="unicode_escape") as tempFile:
            tempFile.write(sentence)
            tempFile.close()

        sentence_vectorized = vectorizer.transform([temp_file_name]) # The vectorizer needs files
        sentence_vectorized = ss.csr_matrix(sentence_vectorized)
        words = list(np.asarray(vectorizer.get_feature_names()))
        not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
        sentence_vectorized = sentence_vectorized[:,not_digit_inds]

        sentence_binary_predictions = topic_model.predict(sentence_vectorized)
        sentence_probabilities = topic_model.predict_proba(sentence_vectorized)[0][0]

        likely_sentence_topics = np.nonzero(sentence_binary_predictions == True)[1]

        for topic_num in likely_sentence_topics: 
            sentence_polarity = TextBlob(sentence).sentiment.polarity
            weighted_score = sentence_polarity * sentence_probabilities[topic_num]
            try:
                topic_sentiment_scores[topic_num] += weighted_score
            except:
                topic_sentiment_scores[topic_num] = weighted_score

        for topic_num,topic_sentiment in topic_sentiment_scores.items():
            if topic_sentiment > 1:
                topic_sentiment_scores[topic_num] = 1
            elif topic_sentiment < -1:
                topic_sentiment_scores[topic_num] = -1
    
    topic_sentiment_scores = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in topic_sentiment_scores.items()])
  
    topic_sentiment_scores_encoded = ", ".join([topic + " = " + str(score) for topic, score in topic_sentiment_scores.items()])        

    try:
        os.remove(temp_file_name)
    except:
        print("Couldn't delete " + temp_file_name)

    try:
        response = parties_table.put_item(
            Item={
                'party-name': current_political_party,
                'top_words': top_words,
                'topics_sentiment_matrix': topic_sentiment_scores_encoded
            }
        )
    except Exception as e:
        print (e)
        print ("Failed for " + current_political_party)