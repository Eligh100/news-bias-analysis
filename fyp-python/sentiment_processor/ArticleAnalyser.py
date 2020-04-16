import os
import csv
import re
import numpy as np
import pandas as pd
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

        topic_model_path = "assets/model/topic_model.pkl"
        topic_vectorizer_path = "assets/model/topic_vectorizer.pkl"

        party_model_path = "assets/model/party_model.pkl"
        party_vectorizer_path = "assets/model/party_vectorizer.pkl"

        try:
            self.topic_model = cPickle.load(open(topic_model_path, 'rb'))
        except Exception as e:
            log_line = "Model: " + topic_model_path + " not found"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        try:
            self.topic_vectorizer = cPickle.load(open(topic_vectorizer_path, "rb"))
        except Exception as e:
            log_line = "Vectorizer: " + topic_vectorizer_path + " not found"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        try:
            self.party_model = cPickle.load(open(party_model_path, 'rb'))
        except Exception as e:
            log_line = "Model: " + party_model_path + " not found"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        try:
            self.party_vectorizer = cPickle.load(open(party_vectorizer_path, "rb"))
        except Exception as e:
            log_line = "Vectorizer: " + party_vectorizer_path + " not found"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exiting prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        # Open MPs CSV and store results in dict
        self.mps = {}
        try:
            with open("assets/political-people.csv") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    self.mps[row[0]] = row[1]
        except Exception as e:
            log_line = "Reading of MPs CSV file at: assets/political-people.csv failed"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            self.logger.writeToLog(log_line, False)

        # Used to track entities throughout the article (i.e. if 'Boris Johnson' appears, then just 'Johnson' should equate to 'Conservative' when seen later)
        self.entity_tracker = {}
        
    def analyseArticleSentiment(self, for_topics):
        
        model = ""
        vectorizer = ""

        if (for_topics):
            model = self.topic_model
            vectorizer = self.topic_vectorizer
        else:
            model = self.party_model
            vectorizer = self.party_vectorizer

        # Store the original text, for use later
        original_text = self.article_text 

        tempFileName = "temp_files/tempProcessing2.txt"

        # Next, find overall most likely topics
        text_vectorized = self.getVectorised(self.article_filename, vectorizer)
        topic_binary_predictions = model.predict(text_vectorized)

        likely_topics = np.nonzero(topic_binary_predictions == True)[1]

        # Create dictionary, key: topic index, value: sentiment scores
        topic_sentiment_scores = {}

        # Then, split the original text into paragraphs and find the most likely topics
        paragraphs = original_text.split("\n")

        # Only consider a paragraph if it has five or more sentences
        # If it doesn't, collate paragraphs into bigger paragraphs
        composite_paragraph = ""

        for paragraph in paragraphs:

            original_paragraph = paragraph

            if composite_paragraph != "":
                paragraph = composite_paragraph + paragraph
            
            sentences = sent_tokenize(paragraph)

            if (len(sentences) < 5):
                composite_paragraph += original_paragraph + "\n"
                continue
            else:
                composite_paragraph = ""

            try:
                with open(tempFileName, "w", encoding="unicode_escape") as tempFile:
                    tempFile.write(paragraph)
                    tempFile.close()
            except Exception as e:
                log_line = "Failed to write to file: " + tempFileName 
                log_line += "\nFailed with the folowing exception:\n"
                log_line += str(e)
                log_line += "\nScript exited prematurely - "
                self.logger.writeToLog(log_line, True)
                exit(0)
            
            paragraph_vectorized = self.getVectorised(tempFileName, vectorizer) 
            paragraph_binary_predictions = model.predict(paragraph_vectorized)
            paragraph_probabilities = model.predict_proba(paragraph_vectorized)[0][0]

            likely_paragraph_topics = np.nonzero(paragraph_binary_predictions == True)[1]
            paragraph_probabilities = dict([(paragraph_index, round(paragraph_probabilities[paragraph_index], 1)) for paragraph_index in range(0, len(paragraph_probabilities)) if paragraph_index in likely_paragraph_topics])

            for topic in likely_paragraph_topics:
                if (topic not in topic_sentiment_scores):
                    topic_sentiment_scores[topic] = 0

            # Next, get sentiment of each sentence
            for sentence in sentences:
                # Get the polarity of the sentence
                sentence_polarity = TextBlob(sentence).sentiment.polarity

                # If the sentence is likely talking about a topic found in the current paragraph, store weighted sentiment
                for topic_num in likely_paragraph_topics:
                    # Get the probability of it being that topic
                    paragraph_topic_weighting = paragraph_probabilities[topic_num]

                    # Weight the polarity by the likelihood of the topic
                    weighted_polarity = sentence_polarity * paragraph_topic_weighting
                    topic_sentiment_scores[topic_num] += weighted_polarity

                # Following code deals with party entities (i.e. MPs), so skip if dealing with topic sentiment
                if (not for_topics):

                    # Change to lower-case and strip accents
                    preprocessed_sentence = self.preprocessor.changeToLower(sentence)
                    preprocessed_sentence = self.preprocessor.stripAccents(sentence)

                    # Check the entity tracker first, if we've already seen an MP previously
                    for full_name, name_split in self.entity_tracker.items():
                        search_forename = re.search(rf".*{name_split[0]}.*", preprocessed_sentence, re.IGNORECASE)
                        search_surname = re.search(rf".*{name_split[1]}.*", preprocessed_sentence, re.IGNORECASE)
                        search_full = re.search(rf".*{full_name}.*", preprocessed_sentence, re.IGNORECASE)

                        if ((search_forename or search_surname) and not search_full): # If either parts of the name appear (but not together)
                            party_num = name_split[2]
                            party_num = int(party_num)
                            if (party_num not in topic_sentiment_scores):
                                topic_sentiment_scores[party_num] = 0
                            topic_sentiment_scores[party_num] += sentence_polarity

                    # If the sentence contains an MP from a political party, get sentiment 
                    for mp_name, party_num in self.mps.items():
                        party_num = int(party_num)
                        search = re.search(rf".*{mp_name}.*", preprocessed_sentence, re.IGNORECASE)
                        if (search):
                            if (party_num not in topic_sentiment_scores):
                                topic_sentiment_scores[party_num] = 0
                            topic_sentiment_scores[party_num] += sentence_polarity

                            # Separate first and last name for advanced entity searching in future sentences in paragraph
                            if (mp_name not in self.entity_tracker):
                                self.entity_tracker[mp_name] = [mp_name.split(" ")[0], mp_name.split(" ")[1], party_num]

        # Returned object, key: topic index, value: score
        articleTopicSentimentsMatrix = {}

        # Once the text has been fully analysed, bound the sentiment scores
        for topic_index, sentiment_score in topic_sentiment_scores.items():
            if (topic_index != 0):
                if (sentiment_score > 1):
                    sentiment_score = 1
                elif (sentiment_score < -1):
                    sentiment_score = -1
                articleTopicSentimentsMatrix[topic_index] = sentiment_score

        try:
            os.remove(tempFileName)
        except Exception as e:
            log_line = "Failed to remove temp file at: " + tempFileName
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            self.logger.writeToLog(log_line, False)

        # Return list of pairs of topic/party and overall sentiment score (for article)
        return (likely_topics, articleTopicSentimentsMatrix)

    def analyseManifestoSimilarity(self):
        
        # First, preprocess the article text
        text = self.article_text
        text = self.preprocessor.changeToLower(text)
        text = self.preprocessor.replaceNewline(text, ' ')
        text = self.preprocessor.removeStopWords(text)
        text = self.preprocessor.stripAccents(text)
        text = self.preprocessor.removeSpecialChars(text)
        words = self.preprocessor.tokenizeWords(text)
        preprocessed_text = self.preprocessor.useOriginalWords(words)

        # Gather processed manifesto texts
        similarityTexts = [preprocessed_text]

        try:
            for manifestoProcessed in os.listdir('manifesto_scraper/manifestosProcessed'):
                manifestoFilePath = "manifesto_scraper/manifestosProcessed/" + manifestoProcessed
                with open(manifestoFilePath , "r", encoding="utf-8") as manifestoTextFile:
                    manifestoText = manifestoTextFile.read()
                    similarityTexts.append(manifestoText)
        except Exception as e:
            log_line = "Unable to locate manifestos"
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        # Perform TF-IDF on article and manifestos
        tfidf_vectorizer = TfidfVectorizer(min_df=1)
        tfidf = tfidf_vectorizer.fit_transform(similarityTexts)
        pairwise_similarity = tfidf * tfidf.T

        # Find cosine similarity, and say two most similar (?)
        n, _ = pairwise_similarity.shape                                                                                                                                                                                                                         
        pairwise_similarity[np.arange(n), np.arange(n)] = -1.0
        most_similar_manifesto = pairwise_similarity[0].argmax() # 0 is the index of the article - so compares to all manifestos

        return PoliticalPartyHelper.PoliticalParty(most_similar_manifesto)

    def analyseHeadlineSentiment(self, for_topics):

        if (for_topics):
            model = self.topic_model
            vectorizer = self.topic_vectorizer
        else:
            model = self.party_model
            vectorizer = self.party_vectorizer

        headline = self.headline
        headline_polarity = TextBlob(headline).sentiment.polarity

        # First, get most likely topic/party using model, and extract weighted sentiment (weighting with likelihood)
        tempFileName = "temp_files/tempProcessing.txt"

        try:
            with open(tempFileName, "w", encoding="unicode_escape") as tempFile:
                tempFile.write(headline)
                tempFile.close()
        except Exception as e:
            log_line = "Failed to write to file: " + tempFileName 
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)

        # Find the most likely topic of the headline
        headline_vectorized = self.getVectorised(tempFileName, vectorizer)
        topic_binary_predictions = model.predict(headline_vectorized)
        topic_probabilities = model.predict_proba(headline_vectorized)[0][0]

        likely_topics = np.nonzero(topic_binary_predictions == True)[1]
        topic_probabilities = dict([(topic_index, round(topic_probabilities[topic_index], 1)) for topic_index in range(0, len(topic_probabilities)) if topic_index in likely_topics])

        headline_topics_matrix = {}
        for likely_topic in likely_topics:
            if (likely_topic != 0): # Ignore the junk topic
                weighted_polarity = headline_polarity * topic_probabilities[likely_topic]
                headline_topics_matrix[likely_topic] = weighted_polarity

        # Then, look for political people (entities)
        if (not for_topics):

            # Change to lower-case and strip accents
            preprocessed_headline = self.preprocessor.changeToLower(headline)
            preprocessed_headline = self.preprocessor.stripAccents(headline)

            # Check the entity tracker first, if we've already seen an MP previously
            for full_name, name_split in self.entity_tracker.items():
                search_forename = re.search(rf".*{name_split[0]}.*", preprocessed_headline, re.IGNORECASE)
                search_surname = re.search(rf".*{name_split[1]}.*", preprocessed_headline, re.IGNORECASE)
                search_full = re.search(rf".*{full_name}.*", preprocessed_headline, re.IGNORECASE)

                if ((search_forename or search_surname) and not search_full): # If either parts of the name appear (but not together)
                    party_num = name_split[2]
                    party_num = int(party_num)
                    if (party_num not in headline_topics_matrix):
                        headline_topics_matrix[party_num] = 0
                    headline_topics_matrix[party_num] += headline_polarity

            # If the sentence contains an MP from a political party, get sentiment 
            for mp_name, party_num in self.mps.items():
                party_num = int(party_num)
                search = re.search(rf".*{mp_name}.*", preprocessed_headline, re.IGNORECASE)
                if (search):
                    if (party_num not in headline_topics_matrix):
                        headline_topics_matrix[party_num] = 0
                    headline_topics_matrix[party_num] += headline_polarity

                    # Separate first and last name for advanced entity searching in future sentences in paragraph
                    if (mp_name not in self.entity_tracker):
                        self.entity_tracker[mp_name] = [mp_name.split(" ")[0], mp_name.split(" ")[1], party_num]

        try:
            os.remove(tempFileName)
        except Exception as e:
            log_line = "Failed to remove temp file at: " + tempFileName
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            self.logger.writeToLog(log_line, False)

        # Return dict (key: topic/party num, value = score)
        return headline_topics_matrix

    # Gets top 20 uni/bigrams from article, for word maps
    def getTopWords(self):

         # First, preprocess the article text
        text = self.article_text
        text = self.preprocessor.changeToLower(text)
        text = self.preprocessor.replaceNewline(text, ' ')
        text = self.preprocessor.removeStopWords(text)
        text = self.preprocessor.stripAccents(text)
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

    def getVectorised(self, tempFileName, vectorizer):
        text_vectorized = vectorizer.transform([tempFileName]) # The vectorizer needs text files, not strings
        text_vectorized = ss.csr_matrix(text_vectorized)
        words = list(np.asarray(vectorizer.get_feature_names()))
        not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
        text_vectorized = text_vectorized[:,not_digit_inds]

        return text_vectorized
        


