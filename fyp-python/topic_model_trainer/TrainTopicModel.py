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

new_model_choice = input("New model (n), or existing (e)? ")

if (new_model_choice == "n"):

    # vectorise the top 20,000 words
    vectorizer = CountVectorizer(input='filename', encoding="unicode_escape", max_features=20000, binary=True, ngram_range=(1,2), stop_words=stopwords.words('english'))
    model_data_files = os.listdir("assets/model_data/train")
    model_data_files = ["assets/model_data/train/" + data_file for data_file in model_data_files]
    doc_word = vectorizer.fit_transform(model_data_files)
    doc_word = ss.csr_matrix(doc_word)

    words = list(np.asarray(vectorizer.get_feature_names()))
    not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
    doc_word = doc_word[:,not_digit_inds]
    words  = [word for ind,word in enumerate(words) if not word.isdigit()]

    # pickle vectoriser for testing model
    cPickle.dump(vectorizer, open("assets/model-updated/vectorizer.pkl", "wb"))

    NUM_TOPICS = 15 # Determined as most effective number of models (see topics over TC chart)

    # Anchors designed to nudge the model towards measuring specific genres
    anchors = [
        ["facebook", "messenger", "linkedin", "whatsapp", "pinterest", "facebook messenger","messenger messenger","messenger twitter","linkedin copy","new window","email facebook","pinterest","pinterest whatsapp","link","share", "register","log", "social account","inbox register","social","inbox","account","iâ","donâ","itâ", "readers click","letters click","letters theguardian","photo youâ","guardian letters","print edition", "twitter com","pic twitter","pic","journalists"], # Junk
        ["long bailey","rebecca long","bailey","rebecca","keir","starmer","keir starmer","nandy","lisa nandy","lisa", "corbyn","jeremy","jeremy corbyn","labour","labour leader","labour party", "shadow","secretary","mcdonnell","john mcdonnell","shadow chancellor","shadow cabinet","chancellor john", "labour mp", "labour mps"], # Labour party
        ["tories", "prime","boris","johnson","prime minister","boris johnson","prime","minister","mr johnson","johnsonâ", "theresa", "theresa may", "cummings","dominic cummings","downing street","downing","dominic","reshuffle", "matt hancock", "hancock", "ministry","government","ministers","department","ensure","work","department","scheme", "patel","priti","priti patel"], # Conservative party and the Government
        ["liberal","lib","liberal democrats","democrats","lib","dems","lib dems","lib dem", "jo", "swinson", "jo swinson"], # Liberal Democrats
        ["sturgeon","nicola sturgeon","nicola","snp","scotland","independence referendum","independence"], # SNP
        ["ireland","irish","northern ireland", "dup", "sinn", "fein", "sinn fein", "backstop"], # Ireland
        ["eu","agreement","deal","trade","trade deal","brussels","european", "referendum","brexit","leave","remain","farage","nigel","second referendum", "future","11pm","leaving","departure"], # EU and Brexit
        ["cost","tax","pay","spending","investment","budget","plans","economy","funding", "rise","increase","decade","fiscal","fiscal studies"], # Economy and Business
        ["nhs","care", "average","health","hospitals", "hospital"], # Healthcare/NHS
        ["trump","donald","us","president","donald trump","us president","us"], # Foreign Policy/US
        ["allegations","accused","antisemitism","jewish","racism","apologise","women", "anti","anti semitism","semitism","racist","muslim","islamophobia","community","ranks"], # Racism
        ["climate","climate change","climate crisis","emissions","carbon","climate emergency","net zero","zero","crisis"], # Environment/Climate change
        ["court","law","rights","legal","legislation","laws","justice", "investigation","alleged", "incident","police","officers","charges","crown"], # Police/Legal
        ["education", "schools", "school", "teaching", "teachers", "grammar", "academic"], # education
        ["immigration", "border", "australia", "points", "borders", "open", "free movement", "movement"] # Immigration
    ]

    best_model = None

    for i in range(0, 5): # run the model generation 5 times, and pick model with highest TC (total correlation)
            
        topic_model = ct.Corex(n_hidden=15, words=words, max_iter=200, verbose=False, seed=1)
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
    topic_model.save("assets/model-updated/topic_model.pkl", ensure_compatibility=False)
else:
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


doc_word = vectorizer.transform(["assets/model_data/test/www.bbc.co.ukFYPSLASHFYPnewsFYPSLASHFYPelection-2019-50478501.txt"])
doc_word = ss.csr_matrix(doc_word)
words = list(np.asarray(vectorizer.get_feature_names()))
not_digit_inds = [ind for ind,word in enumerate(words) if not word.isdigit()]
doc_word = doc_word[:,not_digit_inds]
words  = [word for ind,word in enumerate(words) if not word.isdigit()]

print (topic_model.predict(doc_word))
topic_probs = topic_model.predict_proba(doc_word)[0]
print(topic_probs)
top_3 = (np.argsort(topic_probs, axis=1)[:,:-3])[::-1]
print(top_3)


