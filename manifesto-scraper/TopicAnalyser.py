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

parties = {
    0: "Brexit Party",
    1: "Conservatives",
    2: "Green",
    3: "Labour",
    4: "Liberal Democrats",
    5: "Plaid Cymru",
    6: "SNP",
    7: "UKIP"
}

# first, gather text for each manifesto

new_model_choice = input("New model (n), or existing (e)? ")

if (new_model_choice == "n"):

    manifestoTexts = []
    porterStemmer = PorterStemmer()
    lemmatizer = WordNetLemmatizer()

    stopWords = stopwords.words('english')

    # then, pre-process (remove stop words and stem) 

    for manifesto in os.listdir('manifestos'):
        manifestoFilePath = "manifestos/" + manifesto
        with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
            text = manifestoText.read()

            text = text.lower() # TODO improve this - entity resolution?
            text = re.sub(r'[^a-zA-Z ]+', '', text) # TODO is this best option?
            words = word_tokenize(text) # TODO better tokenizer? and sentence tokenizer?
            words = [word for word in words if word not in stopWords] # TODO bespoke stopword list? with party names in, for instance

            lemmatizedText = ""
            for w in words:
                lemmatizedText += porterStemmer.stem(w) + " "

            words = " ".join(words)
            
            manifestoTexts.append(words)
            manifestoText.close()

    # vectorise the top 20,000 words
    vectorizer = CountVectorizer(max_features=20000, binary=True, ngram_range=(1,2))
    doc_word = vectorizer.fit_transform(manifestoTexts)
    doc_word = ss.csr_matrix(doc_word)
    words = list(np.asarray(vectorizer.get_feature_names()))

    # pickle vectoriser for testing model
    cPickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

    # Anchors designed to nudge the model towards measuring specific genres
    anchors = [
        ["poverty inequality","playing field", "poor", "poorest", "poverty", "income tax", "tax"], # Poverty/Income Inequality
        ["policing", "prison", "police force", "perpetrators", "racism", "police forces", "places worship", "abusers, ""crime", "knife", "criminals", "police", "terrorist", "terrorism"], # crime and policing
        ["economy", "economics", "exchange rate", "pound", "tariff", "business", "powerhouse", "pounds", "privatisation", "private investment", "deficit", "gdp", "national debt"], # business and economics
        ["education", "schools", "school", "teaching", "teachers", "curriculum", "grammar school", "academic"], # education
        ["nhs", "national health", "hospitals", "nurses", "doctors", "medicine", "privatisation", "privatisation nhs"], # healthcare
        ["brexit" "nodeal brexit", "no deal", "postbrexit", "brussels", "EU", "european union", "eu", "European Union", "sovereignty"], # Brexit
        ["climate change", "climate", "climate emergency", "environment", "fossil fuels", "carbon", "zero carbon", "zerocarbon", "planet", "plastic", "petrol diesel", "plastic waste", "pollution", "petrol", "public transport"], # environment and climate change
        #["housing", "houses", "social housing", "homes", "housebuilding", "housing supply", "affordable"], # housing
        ["pledge", "accessible", "powerful", "policies", "points", "powers", "ability", "politics", "practice", "premium", "prioritise", 
        "processes", "abroad", "preventing", "pregnant", "policy", "playing", "play", "priorities", "platforms", "accept", "ports", 
        "political parties", "political", "places", "per cent", "people face", "politically", "positive", "preserve", "prices", "prioritising",
        "abolish", "principles", "primates", "prevent", "pressure", "prepared", "practices", "possession", "abolishing", "products", "profits", "project", 
        "provides", "publication", "published", "purpose", "proportional", "pfi", "planning system", "politicians", "post", "power", "precious", "prepare", "prevention",
        "able", "rate", "pubs", "provide support", "protection", "protect", "received", "property", "projects", "across uk", "present", "prescription", "pregnancy", 
        "practical", "population", "pressing", "planned"] # FILTER TOPIC - FILLED WITH AMBIGUOUS WORDS
    ]

    docs = ["Brexit Party Manifesto", "Conservative Manifesto", "Green Manifesto", "Labour Manifesto", "Liberal Democrats Manifesto",
            "Plaid Cymru Manifesto", "SNP Manifesto", "UKIP Manifesto"]

    anchors = [
        [a for a in topic if a in words]
        for topic in anchors
    ]

    NUM_TOPICS = 10 # Starting number of topics - will increase as model sees fit

    # Firstly, we'll generate the same model fifty times, and find the best (signified by TC score - higher TC = topics are more informative
    # about the documents) - we'll start with 5 hidden topics

    best_model = None

    for i in range(0, 10): # run the model generation 10 times
            
        model = ct.Corex(
            n_hidden=NUM_TOPICS,
            words = words,
        )

        model = model.fit(
            doc_word,
            words=words,
            docs = docs,
            anchors=anchors,
            anchor_strength=6 # Anchor weighting/reliance
        )

        if (best_model == None or model.tc > best_model.tc):
            best_model = model

    model = best_model
    model.save("topic_model.pkl", ensure_compatibility=False)
else:
    topic_model_path = "topic_model.pkl"
    vectorizer_path = "vectorizer.pkl"
    
    try:
        model = cPickle.load(open(topic_model_path, 'rb'))
    except:
        print("Model: " + topic_model_path + " not found")
        exit(0)

    try:
        vectorizer = cPickle.load(open("vectorizer.pkl", "rb"))
    except:
        print("Vectorizer: " + vectorizer_path + " not found")
        exit(0)

with open("testDoc.txt", "r", encoding="utf-8") as testDoc:
    doc_word = vectorizer.transform([testDoc.read()])
    doc_word = ss.csr_matrix(doc_word)
    print(model.predict(doc_word))
    testDoc.close()


# UNCOMMENT TO PLOT TC (TOPIC CORRELATION)
# plt.figure(figsize=(10,5))
# plt.bar(range(model.tcs.shape[0]), model.tcs, color='#4e79a7', width=0.5)
# plt.xlabel('Topic', fontsize=16)
# plt.ylabel('Total Correlation (TC)', fontsize=16)
# plt.show()

for j, topic_ngrams in enumerate(model.get_topics(n_words=20)):
    topic_ngrams = [ngram[0] for ngram in topic_ngrams] #if ngram[1] > 0]
    print("Topic #{}: {}".format(j+1, ", ".join(topic_ngrams)))

