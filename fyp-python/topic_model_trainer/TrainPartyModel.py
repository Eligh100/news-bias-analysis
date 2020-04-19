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
vectorizer = CountVectorizer(max_features=15000, binary=True, ngram_range=(1,2), stop_words=stopwords.words('english'), strip_accents="unicode")
model_data_files = os.listdir("assets/model_data/train")
model_data_files = ["assets/model_data/train/" + data_file for data_file in model_data_files]

# Comment these lines to remove training the test data (only for final run)
model_test_data_files = os.listdir("assets/model_data/test")
model_test_data_files = ["assets/model_data/test/" + data_file for data_file in model_test_data_files]
model_data_files = model_data_files + model_test_data_files

# Store contents of file in list
data = []
for filepath in model_data_files:
    with open(filepath, "r", encoding="unicode_escape") as f:
        data.append(f.read())
        f.close()

doc_word = vectorizer.fit_transform(data)
doc_word = ss.csr_matrix(doc_word)

words = list(np.asarray(vectorizer.get_feature_names()))
not_digit_inds = [ind for ind,word in enumerate(words) if not any(char.isdigit() for char in word)]
doc_word = doc_word[:,not_digit_inds]
words  = [word for ind,word in enumerate(words) if  not any(char.isdigit() for char in word)]

# pickle vectoriser for testing model
cPickle.dump(vectorizer, open("assets/vectorizer.pkl", "wb"))

NUM_TOPICS = 8 # Determined as most effective number of models (see topics over TC chart)

# Anchors designed to nudge the model towards measuring specific genres
anchors = [
    ["facebook", "messenger", "linkedin", "whatsapp", "pinterest", "facebook messenger","messenger messenger","messenger twitter","linkedin copy","new window","email facebook","pinterest","pinterest whatsapp","link","share", "register","log", "social account","inbox register","social","inbox","account", "readers click","letters click","letters theguardian","guardian letters","print edition", "twitter com","pic twitter","pic","journalists"], # Junk
    ["labour","corbyn","jeremy","jeremy corbyn", "long bailey","rebecca long","bailey","rebecca","keir","starmer","keir starmer","nandy","lisa nandy","lisa","labour leader","labour party", "shadow","mcdonnell","john mcdonnell","shadow chancellor","shadow cabinet","chancellor john", "labour mp", "labour mps", "tony blair", "blair", "momentum"], # Labour party
    ["conservative", "conservatives","tories", "tory","boris","johnson","prime minister","boris johnson","prime","minister","mr johnson", "theresa", "theresa may", "cummings","dominic cummings","downing street","downing","dominic", "matt hancock", "hancock", "ministry","government","ministers", "patel","priti","priti patel", "david cameron", "cameron"], # Conservative party and the Government
    ["liberal democrats", "liberal","lib","lib","dems","lib dems","lib dem", "jo", "swinson", "jo swinson"], # Liberal Democrats
    ["snp","sturgeon","scottish national","nicola sturgeon","nicola","independence referendum", "holyrood", "ian blackford", "blackford"], # SNP
    ["green party", "green", "sian", "berry", "jonathan bartley", "bartley", "caroline lucas", "lucas", "brighton", "greens"], # Green
    ["brexit party","farage","nigel", "nigel farage", "ann widdecombe", "widdecombe", "tice", "richard tice"], # Brexit Party
    ["plaid cymru", "plaid", "cymru", "adam price"], # Plaid Cymru
]

best_model = None

for i in range(0, 5): # run the model generation 5 times, and pick model with highest TC (total correlation)
        
    model = ct.Corex(n_hidden=NUM_TOPICS, words=words, max_iter=200, verbose=False, seed=1)
    model.fit(doc_word, words=words, anchors=anchors, anchor_strength=5)

    # UNCOMMENT TO PLOT TC (TOPIC CORRELATION)
    # plt.figure(figsize=(10,5))
    # plt.bar(range(model.tcs.shape[0]), model.tcs, color='#4e79a7', width=0.5)
    # plt.xlabel('Topic', fontsize=16)
    # plt.ylabel('Total Correlation (TC)', fontsize=16)
    # plt.show()

    if (best_model == None or model.tc > best_model.tc):
        best_model = model

model = best_model

# Print all parties from the CorEx topic model
# topics = model.get_topics()
# for n,topic in enumerate(topics):
#     topic_words,_ = zip(*topic)
#     print('{}: '.format(n) + ','.join(topic_words))

model.save("assets/model/party_model.pkl", ensure_compatibility=False)
