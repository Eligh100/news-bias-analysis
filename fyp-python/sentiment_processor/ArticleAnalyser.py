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

    def __init__(self, logger, article_text, headline, preprocessor):
        self.logger = logger
        self.article_text = article_text
        self.headline = headline
        self.preprocessor = preprocessor

        topic_model_path = "assets/model/topic_model.pkl"
        vectorizer_path = "assets/model/vectorizer.pkl"

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
        preprocessed_text = self.preprocessor.removeStopWords(preprocessed_text)
        preprocessed_text = self.preprocessor.removeSpecialChars(preprocessed_text)
        words = self.preprocessor.tokenizeWords(preprocessed_text)
        preprocessed_text = self.preprocessor.lemmatizeText(words)

        # Next, find overall most likely topics
        text_vectorized = self.vectorizer.transform([preprocessed_text])
        text_vectorized = ss.csr_matrix(text_vectorized)
        topic_predictions = self.model.predict(text_vectorized)
        print(topic_predictions)

        likely_topics = [topic_index for topic_index in range(len(topic_predictions[0])) if topic_predictions[0][topic_index] == True]

        # Then, sentence split on original (unprocessed) text and find sentences related to these topics
        sentences = sent_tokenize(original_text)

        topicSentimentScores = {
            0:[0,0], 1:[0,0], 2:[0,0], 3:[0,0], 4:[0,0],
            5:[0,0], 6:[0,0], 7:[0,0], 8:[0,0], 9:[0,0]
        }

        for sentence in sentences:
            sentence_vectorized = self.vectorizer.transform([sentence])
            sentence_vectorized = ss.csr_matrix(sentence_vectorized)
            sentence_predictions = self.model.predict(sentence_vectorized)

            likely_sentence_topics = [topic_index for topic_index in range(len(sentence_predictions[0])) if sentence_predictions[0][topic_index] == True]

            shared_topics = [topic for topic in likely_topics if topic in likely_sentence_topics]

            # If the sentence is likely talking about a topic found in the overall article, get sentiment
            for topic_num in shared_topics: 
                sentencePolarity = TextBlob(sentence).sentiment.polarity
                topicSentimentScores[topic_num][0] += sentencePolarity
                topicSentimentScores[topic_num][1] += 1

        articleTopicSentimentsMatrix = []

        mostCounts = 0
        self.main_topic = -1

        # Once all sentences have been analysed, get mean of sentiment scores
        for topic_index, sentimentScoreAndCounter in topicSentimentScores.items():
            sentimentScore = sentimentScoreAndCounter[0]
            sentimentCounter = sentimentScoreAndCounter[1]
            if (sentimentCounter > 0):
                if sentimentCounter > mostCounts:
                    mostCounts = sentimentCounter
                    self.main_topic = topic_index

                topicSentimentScores[topic_index][0] = sentimentScore / sentimentCounter
                articleTopicSentimentsMatrix.append((topic_index, topicSentimentScores[topic_index][0]))

        # Return list of pairs of topic, and overall sentiment score (from article)
        return articleTopicSentimentsMatrix
 
    # i.e. mentions of "Labour", "Jeremy Corbyn", "Momentum", etc. - use MPs.csv, and own domain knowledge
    def analyseEntitySentiment(self):
        # Use the unprocessed text, as entity information can be lost (i.e. removal of capital letters)
        text = self.article_text

    def analyseManifestoSimilarity(self): # TODO test this
        
        # First, preprocess the article text
        text = self.article_text
        text = self.preprocessor.changeToLower(text)
        text = self.preprocessor.replaceNewline(text, ' ')
        text = self.preprocessor.removeStopWords(text)
        text = self.preprocessor.removeSpecialChars(text)
        words = self.preprocessor.tokenizeWords(text)
        preprocessed_text = self.preprocessor.useOriginalWords(words)

        # Gather processed manifesto texts
        similarityTexts = [preprocessed_text]

        for manifestoProcessed in os.listdir('manifesto_scraper/manifestosProcessed'):
            manifestoFilePath = "manifesto_scraper/manifestosProcessed/" + manifestoProcessed
            with open(manifestoFilePath , "r", encoding="utf-8") as manifestoTextFile:
                manifestoText = manifestoTextFile.read()
                similarityTexts.append(manifestoText)

        # Perform TF-IDF on article and manifestos
        tfidf_vectorizer = TfidfVectorizer(min_df=1)
        tfidf = tfidf_vectorizer.fit_transform(similarityTexts)
        pairwise_similarity = tfidf * tfidf.T

        # Find cosine similarity, and say two most similar (?)
        n, _ = pairwise_similarity.shape                                                                                                                                                                                                                         
        pairwise_similarity[np.arange(n), np.arange(n)] = -1.0
        most_similar_manifesto = pairwise_similarity[0].argmax() # 0 is the index of the article - so compares to all manifestos

        return PoliticalParty(most_similar_manifesto)

    def analyseHeadlineSentiment(self):
        headline = self.headline
        headline_polarity = TextBlob(headline).sentiment.polarity

        print(headline_polarity)

        # headline_vectorized = self.vectorizer.transform([headline])
        # headline_vectorized = ss.csr_matrix(headline_vectorized)
        # headline_prediction = self.model.predict_proba(headline_vectorized)

        # Thus, headline has x polarity, about the article's topic (store this in DynamoDB)
        return ((self.main_topic, headline_polarity))


    # Gets top 20 uni/bigrams from article, for word maps
    def getTopWords(self):

         # First, preprocess the article text
        text = self.article_text
        text = self.preprocessor.changeToLower(text)
        text = self.preprocessor.replaceNewline(text, ' ')
        text = self.preprocessor.removeStopWords(text)
        text = self.preprocessor.removeSpecialChars(text)
        words = self.preprocessor.tokenizeWords(text)
        preprocessed_text = self.preprocessor.useOriginalWords(words)

        # Then, vectorize, and get the top 20 words (word frequency)
        vectorizer = CountVectorizer(ngram_range=(1,2))
        vectors = vectorizer.fit_transform([preprocessed_text])
        feature_names = vectorizer.get_feature_names()
        dense = vectors.todense()
        denselist = dense.tolist()
        df = pd.DataFrame(denselist, columns=feature_names)
        top_words = df.iloc[[0]].sum(axis=0).sort_values(ascending=False)
        return top_words[0:20]

    def calculateBiasScore(self): 
        print("") # TODO implement me
        


