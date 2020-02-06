'''
LDA to get topics - and then go back into text and extract sentiment about said topics?
Combine this with keyword extraction
'''


import os
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.decomposition import NMF, LatentDirichletAllocation
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt 
import pandas as pd
import re


def display_topics(model, feature_names, no_top_words):
    for topic_idx , topic in enumerate(model.components_):
        print("Topic %d:" % (topic_idx))
        print(" ".join([feature_names[i] for i in topic.argsort()[:-no_top_words -1:-1]]))

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

# then, pre-process (remove stop words and stem)   WENZELS

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
            lemmatizedText += lemmatizer.lemmatize(w) + " "

        words = " ".join(words)
        
        manifestoTexts.append(words)
        manifestoText.close()

no_features = 1000
tfidf_vectorizer = TfidfVectorizer(max_df = 0.95, min_df = 2,max_features=no_features, ngram_range=(1,1))
tfidf = tfidf_vectorizer.fit_transform(manifestoTexts)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()

no_topic = 7
counter = 0
for i in tfidf:
    print("\n\n\n")
    print(parties[counter])
    counter += 1
    #nmf = NMF(n_components=no_topic, random_state = 1, alpha =.1, l1_ratio=.5, init = 'nndsvd').fit(tfidf)
    lda = LatentDirichletAllocation(n_components=no_topic, max_iter = 5, learning_method = 'online', learning_offset=50., random_state=0).fit(i)

    display_topics(lda , tfidf_feature_names , 10)

    
