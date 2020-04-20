import os
import re
import numpy as np
import pandas as pd
import tkinter
import matplotlib
import matplotlib.pyplot as plt
import scipy.sparse as ss
import _pickle as cPickle
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics import f1_score
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF, LatentDirichletAllocation
from corextopic import corextopic as ct
from corextopic import vis_topic as vt

matplotlib.use('TkAgg') # to display topic graphs

topic_model_path = "assets/model/topic_model.pkl"
vectorizer_path = "assets/vectorizer.pkl"

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

# Model predicts numerous probabilities
# User has labelled with most likely topic, which is converted to number (1-12 - topic index)
# If model.predict yields true for this topic, get predict_proba for this
# If false, score of 0 is given
# Score is given based on predict_proba score - best is 1
# If all the topics are low scorers for a given article, if the user guesses it, they get a 1
# But, if there's some that are 1, and the user labels it as the main topic, the score is lowered
#   This is because the model hasn't predicted the best topic accurately, but still noted the topic's usage
# Keep to 1 decimal place, round up - clearer that way

test_files = os.listdir("assets/model_data/small_test")
test_files = ["assets/model_data/small_test/" + test_file for test_file in test_files]
test_files_labels = [int(test_file[30:32]) for test_file in test_files]

total = len(test_files_labels)

# Store contents of file in list
data = []
for filepath in test_files:
    with open(filepath, "r", encoding="unicode_escape") as f:
        data.append(f.read())
        f.close()

doc_word = vectorizer.transform(data)
doc_word = ss.csr_matrix(doc_word)
words = list(np.asarray(vectorizer.get_feature_names()))
not_digit_inds = [ind for ind,word in enumerate(words) if not any(char.isdigit() for char in word)]
doc_word = doc_word[:,not_digit_inds]
words  = [word for ind,word in enumerate(words) if  not any(char.isdigit() for char in word)]

binary_predictions = topic_model.predict(doc_word)
probability_predictions = topic_model.predict_proba(doc_word)[0]

score = 0 

true_positives = 0
false_positives = 0
false_negatives = 0

shared_index = -1
for binary_prediction, probability_prediction in zip(binary_predictions, probability_predictions):
    shared_index += 1
    likely_topics = np.nonzero(binary_prediction == True)

    labelled_topic = test_files_labels[shared_index]

    if (labelled_topic == 0):
        if (not np.any(binary_prediction)):
            true_positives += 1
            score += 1
        else:
            false_positives += 1
            false_negatives += 1
    else:
        if (binary_prediction[labelled_topic] == True):
            rounded_score = round(probability_prediction[labelled_topic], 1)
            score += rounded_score
            true_positives += 1
        else:
            false_positives += 1
            false_negatives += 1
            #pass
            # print("File:")
            # print(test_files[shared_index])
            # print("\nMy guess:")
            # print(labelled_topic)
            # print("Predictions:")
            # print(binary_prediction)
            # print("Probabilities: ")
            # print(probability_prediction)

print(str(score) + "/" + str(total))
print("Accuracy of: " + str((score/total)*100) + "%\n")  

print("TP = " + str(true_positives))
print("FP = " + str(false_positives))
print("FN = " + str(false_negatives))
print("\n")

precision = true_positives / (true_positives + false_positives)
recall = true_positives / (true_positives + false_negatives)
f1 = 2 * (precision * recall) / (precision + recall)

print ("Precision = " + str(precision))
print ("Recall = " + str(recall))
print ("F1 = " + str(f1))


# # print (topic_model.predict(doc_word))
# # topic_probs = topic_model.predict_proba(doc_word)[0]
# # print(topic_probs)
# # top_3 = (np.argsort(topic_probs, axis=1)[:,:-3])[::-1]
# # print(top_3)