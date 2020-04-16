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
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF, LatentDirichletAllocation
from corextopic import corextopic as ct
from corextopic import vis_topic as vt

matplotlib.use('TkAgg') # to display topic graphs


# vectorise the top 1,000 words
vectorizer = CountVectorizer(input='filename', encoding="unicode_escape", max_features=1000, binary=True, ngram_range=(1,2), stop_words=stopwords.words('english'), strip_accents="unicode")
model_data_files = os.listdir("assets/model_data/train")
model_data_files = ["assets/model_data/train/" + data_file for data_file in model_data_files]

# Comment these lines to remove training the test data (only for final run)
# model_test_data_files = os.listdir("assets/model_data/test")
# model_test_data_files = ["assets/model_data/test/" + data_file for data_file in model_test_data_files]
# model_data_files = model_data_files + model_test_data_files

doc_word = vectorizer.fit_transform(model_data_files)
doc_word = ss.csr_matrix(doc_word)

words = list(np.asarray(vectorizer.get_feature_names()))
not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
doc_word = doc_word[:,not_digit_inds]
words  = [word for ind,word in enumerate(words) if not word.isdigit()]

# pickle vectoriser for testing model
cPickle.dump(vectorizer, open("assets/model/party_vectorizer.pkl", "wb"))

NUM_TOPICS = 8 # Determined as most effective number of models (see topics over TC chart)

# Anchors designed to nudge the model towards measuring specific genres
anchors = [
    ["facebook", "messenger", "linkedin", "whatsapp", "pinterest", "facebook messenger","messenger messenger","messenger twitter","linkedin copy","new window","email facebook","pinterest","pinterest whatsapp","link","share", "register","log", "social account","inbox register","social","inbox","account","iâ","donâ","itâ", "readers click","letters click","letters theguardian","photo youâ","guardian letters","print edition", "twitter com","pic twitter","pic","journalists"], # Junk
    ["labour","corbyn","jeremy","jeremy corbyn", "long bailey","rebecca long","bailey","rebecca","keir","starmer","keir starmer","nandy","lisa nandy","lisa","labour leader","labour party", "shadow","secretary","mcdonnell","john mcdonnell","shadow chancellor","shadow cabinet","chancellor john", "labour mp", "labour mps", "welsh labour", "scottish labour", "tony blair", "blair", "labours", "momentum"], # Labour party
    ["conservative", "conservatives","tories", "prime","boris","johnson","prime minister","boris johnson","prime","minister","mr johnson","johnsonâ", "theresa", "theresa may", "cummings","dominic cummings","downing street","downing","dominic","reshuffle", "matt hancock", "hancock", "ministry","government","ministers","department","ensure","work","department","scheme", "patel","priti","priti patel", "scottish conservatives", "welsh conservative", "scottish conservative", "david cameron", "cameron"], # Conservative party and the Government
    ["liberal democrats", "liberal","lib","lib","dems","lib dems","lib dem", "jo", "swinson", "jo swinson"], # Liberal Democrats
    ["snp","sturgeon","nicola sturgeon","nicola","independence referendum","independence", "holyrood", "ian blackford", "blackford", "alex salmond", "salmond"], # SNP
    ["green party", "green", "sian berry", "berry", "jonathan bartley", "bartley", "caroline lucas", "lucas", "brighton pavilion", "greens"], # Green
    ["brexit party","farage","nigel", "nigel farage", "ann widdecombe", "widdecombe", "tice", "richard tice"], # Brexit Party
    ["plaid cymru", "plaid", "cymru", "wales", "welsh", "assembly", "welsh assembly", "cardiff", "adam price"], # Plaid Cymru
]

best_model = None

for i in range(0, 5): # run the model generation 5 times, and pick model with highest TC (total correlation)
        
    topic_model = ct.Corex(n_hidden=NUM_TOPICS, words=words, max_iter=200, verbose=False, seed=1)
    topic_model.fit(doc_word, words=words, anchors=anchors, anchor_strength=5)

    # UNCOMMENT TO PLOT TC (TOPIC CORRELATION)
    # plt.figure(figsize=(10,5))
    # plt.bar(range(topic_model.tcs.shape[0]), topic_model.tcs, color='#4e79a7', width=0.5)
    # plt.xlabel('Topic', fontsize=16)
    # plt.ylabel('Total Correlation (TC)', fontsize=16)
    # plt.show()

    if (best_model == None or topic_model.tc > best_model.tc):
        best_model = topic_model

topic_model = best_model
topic_model.save("assets/model/party_model.pkl", ensure_compatibility=False)
