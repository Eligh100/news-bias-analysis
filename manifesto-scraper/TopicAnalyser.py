'''
LDA to get topics - and then go back into text and extract sentiment about said topics?
Combine this with keyword extraction
'''


import os
import scipy.sparse as ss
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF, LatentDirichletAllocation
from corextopic import corextopic as ct
import pandas as pd
import numpy as np
import re

def display_topics(model, feature_names, no_top_words):
    for topic_idx , topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(", ".join([feature_names[i] for i in topic.argsort()[:-no_top_words -1:-1]]))

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


vectorizer = CountVectorizer(max_features=20000, binary=True)
doc_word = vectorizer.fit_transform(manifestoTexts)
doc_word = ss.csr_matrix(doc_word)
print(doc_word.shape)
words = list(np.asarray(vectorizer.get_feature_names()))
#tfidf_vectorizer = TfidfVectorizer(min_df = 0.5, max_df = 10, ngram_range=(1,2))
#tfidf = tfidf_vectorizer.fit_transform(manifestoTexts)
#tfidf_feature_names = tfidf_vectorizer.get_feature_names()




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

model = ct.Corex(
    n_hidden=8,
    words = words,
)
model = model.fit(
    doc_word,
    words=words,
    docs = docs,
    anchors=anchors,
    anchor_strength=6 # Anchor weighting/reliance
)


#print(model.p_y_given_x)
#print(model.get_top_docs(topic=0, n_docs=8, sort_by="log_prob"))

for j, topic_ngrams in enumerate(model.get_topics(n_words=20)):
    topic_ngrams = [ngram[0] for ngram in topic_ngrams] #if ngram[1] > 0]
    print("Topic #{}: {}".format(j+1, ", ".join(topic_ngrams)))





# USE COREX - SEMI-SUPERVISED LEARNING TECHNIQUE
    
'''
Use CorEx topics WITHOUT anchor words first
See general topic distribution
Then, add anchor words from first list, and from manifestos
Test on manifestos and some hand-picked articles - DOCUMENT THIS PROCESS
'''