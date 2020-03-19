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

# vectorise the top 20,000 words
vectorizer = CountVectorizer(input='filename', encoding="unicode_escape", max_features=1500, binary=True, ngram_range=(1,2), stop_words=stopwords.words('english'))
model_data_files = os.listdir("assets/model_data/train")
model_data_files = ["assets/model_data/train/" + data_file for data_file in model_data_files]

# Comment these lines to remove training the test data (only for final run)
model_test_data_files = os.listdir("assets/model_data/test")
model_test_data_files = ["assets/model_data/test/" + data_file for data_file in model_test_data_files]
model_data_files = model_data_files + model_test_data_files

doc_word = vectorizer.fit_transform(model_data_files)
doc_word = ss.csr_matrix(doc_word)

words = list(np.asarray(vectorizer.get_feature_names()))
not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
doc_word = doc_word[:,not_digit_inds]
words  = [word for ind,word in enumerate(words) if not word.isdigit()]

# pickle vectoriser for testing model
cPickle.dump(vectorizer, open("assets/model-final/topic_vectorizer.pkl", "wb"))

NUM_TOPICS = 13 # Determined as most effective number of models (see topics over TC chart)

# Anchors designed to nudge the model towards measuring specific genres
anchors = [
    ["facebook", "messenger", "linkedin", "whatsapp", "pinterest", "facebook messenger","messenger messenger","messenger twitter","linkedin copy","new window","email facebook","pinterest","pinterest whatsapp","link","share", "register","log", "social account","inbox register","social","inbox","account","iâ","donâ","itâ", "readers click","letters click","letters theguardian","photo youâ","guardian letters","print edition", "twitter com","pic twitter","pic","journalists", "liveblog"], # Junk
    ["sturgeon","nicola sturgeon","nicola","snp","scotland","independence referendum","independence", "holyrood", "edinburgh", "second independence"], # Scotland
    ["ireland","irish","northern ireland", "dup", "sinn", "fein", "sinn fein", "backstop", "dublin", "belfast", "stormont"], # Ireland
    ["wales", "welsh", "assembly", "plaid", "cymru", "plaid cymru", "cardiff", "swansea"], # Wales
    ["eu","agreement","deal","trade","trade deal","brussels","european", "referendum","brexit", "european union","leave","remain","farage","nigel","second referendum", "future","11pm","leaving","departure", "tariff", "fishing", "barnier", "juncker", "commission", "european commission"], # EU and Brexit
    ["cost","tax","pay","spending","investment","budget","plans","economy","funding", "rise","increase","decade","fiscal","fiscal studies", "poverty", "council", "housebuilding", "housing", "shortage", "austerity", "duty", "privatisation", "privatised", "privatise", "union"], # Economy and Business
    ["nhs", "average","health","hospitals", "hospital", "virus", "social care", "care", "mental illness", "illness", "privatisation", "privatised", "privatise","drugs", "welfare", "benefit", "disability"], # Healthcare/NHS and Welfare
    ["trump","donald","us","president","donald trump", "washington", "us president","us", "china", "chinese", "israel", "india", "canada", "saudi arabia", "australia", "foreign", "foreign policy", "putin", "russia", "merkel", "germany", "macron", "france"], # Foreign Policy/US
    ["allegations","accused","antisemitism","jewish","racism","apologise","women", "anti","anti semitism","semitism","racist","muslim","islamophobia","community","ranks", "minority", "terrorism", "terrorist", "transphobic", "black", "terror", "misogyny", "misogynist", "feminism", "feminist", "racial", "windrush", "deportation", "black people"], # Racism/ Hate crime
    ["climate","climate change","climate crisis","emissions","carbon","climate emergency","net zero","zero","crisis", "nature", "fossil fuels", "fuel", "fossil", "diesel", "petrol", "polluting", "pollution", "atmosphere", "wildlife", "environment", "environmental", "biodiversity", "natural", "smog"], # Environment/Climate change
    ["court","law","rights","legal","legislation","laws","justice", "investigation","alleged", "incident","police","officers","charges","crown", "jail", "jailed", "prosecutor", "drugs", "stabbings", "knife crime", "knives", "terrorism", "terrorist"], # Police/Legal
    ["education", "schools", "school", "teaching", "teachers", "grammar", "academic", "students", "university", "universities", "tuition fees", "tuition", "student", "ofsted", "curriculum", "erasmus", "college"], # Education
    ["immigration", "border", "australia", "points", "borders", "open", "free movement", "movement", "visas", "visa", "migration", "skill", "skills", "skilled", "migrants", "australian", "deportation", "calais"] # Immigration
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
topic_model.save("assets/model-final/topic_model.pkl", ensure_compatibility=False)


