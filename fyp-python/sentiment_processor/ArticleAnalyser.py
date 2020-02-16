import os
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

from helper_classes.Enums import PoliticalParty

class ArticleAnalyser: # TODO add logging

    topicSentimentScores = {
        0:[0,0],
        1:[0,0],
        2:[0,0],
        3:[0,0],
        4:[0,0],
        5:[0,0],
        6:[0,0],
        7:[0,0],
        8:[0,0],
        9:[0,0]
    }

    chosenPoliticalParty = ""

    partyToManifesto = {
        PoliticalParty.brexitParty : ""
    }

    def __init__(self, logger, article_text, preprocessor):
        self.logger = logger
        self.article_text = article_text
        self.preprocessor = preprocessor

        topic_model_path = "model/topic_model.pkl"
        vectorizer_path = "model/vectorizer.pkl"

        try:
            self.model = cPickle.load(open(topic_model_path, 'rb'))
        except:
            print("Model: " + topic_model_path + " not found")
            exit(0)

        try:
            self.vectorizer = cPickle.load(open(vectorizer_path, "rb"))
        except:
            print("Vectorizer: " + vectorizer_path + " not found")
            exit(0)
    

    def analyseTopicsSentiment(self):

        # First, preprocess the article text
        original_text = self.article_text # Store the original text, for use later
        preprocessed_text = self.article_text

        preprocessed_text = self.preprocessor.changeToLower(preprocessed_text)
        preprocessed_text = self.preprocessor.replaceNewline(preprocessed_text, ' ')
        preprocessed_text = self.preprocessor.removeSpecialChars(preprocessed_text)
        words = self.preprocessor.tokenizeWords(preprocessed_text)
        words = self.preprocessor.removeStopWords(preprocessed_text)
        preprocessed_text = self.preprocessor.lemmatizeText(words)

        # Next, find overall most likely topics
        text_vectorized = self.vectorizer.transform([preprocessed_text])
        text_vectorized = ss.csr_matrix(text_vectorized)
        topic_predictions = self.model.predict(text_vectorized)

        likely_topics = [topic_index for topic_index in range(len(topic_predictions[0])) if topic_predictions[0][topic_index] == True]

        print(likely_topics)

        # Then, sentence split on original (unprocessed) text and find sentences related to these topics
        sentences = sent_tokenize(original_text)

        for sentence in sentences:
            sentence_vectorized = self.vectorizer.transform([sentence])
            sentence_vectorized = ss.csr_matrix(sentence_vectorized)
            sentence_predictions = self.model.predict(sentence_vectorized)

            likely_sentence_topics = [topic_index for topic_index in range(len(sentence_predictions[0])) if sentence_predictions[0][topic_index] == True]
            
            shared_topics = [topic for topic in likely_topics if topic in likely_sentence_topics]

            # If the sentence is likely talking about a topic found in the overall article, get sentiment
            for topic_num in shared_topics: 
                sentencePolarity = TextBlob(sentence).sentiment.polarity
                self.topicSentimentScores[topic_num][0] += sentencePolarity
                self.topicSentimentScores[topic_num][1] += 1

        # Once all sentences have been analysed, get mean of sentiment scores
        for topic_index, sentimentScoreAndCounter in self.topicSentimentScores.items():
            sentimentScore = sentimentScoreAndCounter[0]
            sentimentCounter = sentimentScoreAndCounter[1]
            if (sentimentCounter > 0):
                self.topicSentimentScores[topic_index][0] = sentimentScore / sentimentCounter

    # i.e. mentions of "Labour", "Jeremy Corbyn", "Momentum", etc. - use MPs.csv, and own domain knowledge
    def analyseEntitySentiment(self):
        print("") # TODO implement me

    def analyseManifestoSimilarity(self): # TODO finish implementing TF-IDF on articles/manifesto
        print("")

    def analyseHeadlineSentiment(self, headline):
        print("")# TODO implement me

    def calculateBiasScore(self):
        print("") # TODO implement me
        


