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

from helper_classes.Enums import PoliticalPartyHelper

class ArticleAnalyser: # TODO add logging

    def __init__(self, logger, article_text, article_filename, headline, preprocessor):
        self.logger = logger
        self.article_text = article_text
        self.article_filename = article_filename
        self.headline = headline
        self.preprocessor = preprocessor

        topic_model_path = "assets/model-updated/topic_model.pkl"
        vectorizer_path = "assets/model-updated/vectorizer.pkl"

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
        # preprocessed_text = self.article_text

        # preprocessed_text = self.preprocessor.changeToLower(preprocessed_text)
        # preprocessed_text = self.preprocessor.replaceNewline(preprocessed_text, ' ')
        # preprocessed_text = self.preprocessor.removeStopWords(preprocessed_text)
        # preprocessed_text = self.preprocessor.removeSpecialChars(preprocessed_text)
        # words = self.preprocessor.tokenizeWords(preprocessed_text)
        # preprocessed_text = self.preprocessor.lemmatizeText(words)

        tempFileName = "temp_files/tempProcessing.txt"

        # Next, find overall most likely topics
        text_vectorized = self.getVectorised(self.article_filename)
        topic_binary_predictions = self.model.predict(text_vectorized)
        topic_probabilities = self.model.predict_proba(text_vectorized)[0][0]

        likely_topics = np.nonzero(topic_binary_predictions == True)[1]
        topic_probabilities = dict([(topic_index, round(topic_probabilities[topic_index], 1)) for topic_index in range(0, len(topic_probabilities)) if topic_index in likely_topics])

        # Then, sentence split on original (unprocessed) text and find sentences related to these topics
        sentences = sent_tokenize(original_text)

        topic_sentiment_scores = {}

        for topic in likely_topics:
            topic_sentiment_scores[topic] = 0

        for sentence in sentences:
            with open(tempFileName, "w", encoding="unicode_escape") as tempFile:
                tempFile.write(sentence)
                tempFile.close()

            sentence_vectorized = self.getVectorised(tempFileName) 
            sentence_binary_predictions = self.model.predict(sentence_vectorized)

            likely_sentence_topics = np.nonzero(sentence_binary_predictions == True)[1]

            shared_topics = [topic for topic in likely_topics if topic in likely_sentence_topics]

            # If the sentence is likely talking about a topic found in the overall article, get sentiment
            for topic_num in shared_topics: 
                sentence_polarity = TextBlob(sentence).sentiment.polarity
                topic_sentiment_scores[topic_num] += sentence_polarity

        try:
            os.remove(tempFileName)
        except:
            print("Couldn't delete " + tempFileName)

        articleTopicSentimentsMatrix = {}

        # Once all sentences have been analysed, get weighted sentiment scores
        for topic_index, sentiment_score in topic_sentiment_scores.items():
            overall_topic_weighting = topic_probabilities[topic_index]
            weighted_score = sentiment_score * overall_topic_weighting
            if (weighted_score > 1):
                weighted_score = 1
            elif (weighted_score < -1):
                weighted_score = -1
            articleTopicSentimentsMatrix[topic_index] = weighted_score

        # Return list of pairs of topic and overall sentiment score (for article)
        return (likely_topics, articleTopicSentimentsMatrix)
 
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

        return PoliticalPartyHelper.PoliticalParty(most_similar_manifesto)

    def analyseHeadlineSentiment(self):
        headline = self.headline
        headline_polarity = TextBlob(headline).sentiment.polarity

        tempFileName = "temp_files/tempProcessing.txt"

        with open(tempFileName, "w", encoding="unicode_escape") as tempFile:
            tempFile.write(headline)
            tempFile.close()

        headline_vectorized = self.getVectorised(tempFileName)
        topic_binary_predictions = self.model.predict(headline_vectorized)
        topic_probabilities = self.model.predict_proba(headline_vectorized)[0][0]

        likely_topics = np.nonzero(topic_binary_predictions == True)[1]
        topic_probabilities = dict([(topic_index, round(topic_probabilities[topic_index], 1)) for topic_index in range(0, len(topic_probabilities)) if topic_index in likely_topics])

        headline_topics_matrix = {}
        for likely_topic in likely_topics:
            weighted_polarity = headline_polarity * topic_probabilities[likely_topic]
            headline_topics_matrix[likely_topic] = weighted_polarity

        try:
            os.remove(tempFileName)
        except:
            print("Couldn't delete " + tempFileName)

        # Thus, headline has x polarity, about the article's topic (store this in DynamoDB)
        return headline_topics_matrix


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

    def getVectorised(self, tempFileName):
        text_vectorized = self.vectorizer.transform([tempFileName]) # The vectorizer needs files
        text_vectorized = ss.csr_matrix(text_vectorized)
        words = list(np.asarray(self.vectorizer.get_feature_names()))
        not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
        text_vectorized = text_vectorized[:,not_digit_inds]

        return text_vectorized
        


