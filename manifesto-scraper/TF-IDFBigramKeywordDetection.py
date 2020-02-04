'''
This code uses TF-IDF to cross-reference all party manifestos, and select unique bigrams
In the greater scope of the project, this can be used to add weighting to the overall bias score
    i.e. a paper whose articles involve keywords found in a certain manifesto could have additional bias towards that paper
    Also, papers that discuss topics mentioned in one manifesto more could be noted
This script itself is NOT enough - needs to be combined with a topic analyser that extracts sentiment
For instance, just because a paper mentions brexit a lot, doesn't mean they support the brexit party or the conservatives
Perhaps this script could be adjusted to extract sentimental keywords (i.e. 'betrayal' could imply bias)
'''

import os
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt 
import pandas as pd
import re

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

        # lemmatizedText = ""
        # for w in words:
            #lemmatizedText += lemmatizer.lemmatize(w) + " "

        words = " ".join(words)
        
        manifestoTexts.append(words)
        manifestoText.close()

# finally, perform tf-idf to gather unique keywords for each document

keywords = {}

for i in range(0,7):
    keywords[i] = []
    for j in range(0,7):
        if (i != j): 

            # TF-IDFing
            vectorizer = TfidfVectorizer(ngram_range=(2,2))
            vectors = vectorizer.fit_transform([manifestoTexts[i], manifestoTexts[j]])
            feature_names = vectorizer.get_feature_names()
            dense = vectors.todense()
            denselist = dense.tolist()
            df = pd.DataFrame(denselist, columns=feature_names)
            top_words = df.iloc[[0]].sum(axis=0).sort_values(ascending=False)

            keywords[i].append(top_words[0:20])

totalScoresDict = {}

for partyIndex,partyKeywordList in keywords.items():
    partyName = parties[partyIndex]
    totalScoresDict[partyName] = {}
    for keywordsScoreDict in partyKeywordList:
        for currentKeyword,currentKeywordScore in keywordsScoreDict.items():
            if currentKeyword not in totalScoresDict[partyName]:
                totalScoresDict[partyName][currentKeyword] = 0.0
            totalScoresDict[partyName][currentKeyword] += currentKeywordScore

for party,keywordScores in totalScoresDict.items():
    keywordsFilePath = "bigrams/" + party + "-bigrams.txt"
    with open(keywordsFilePath, "w", encoding="utf-8") as keywordFile:
        for keyword,score in keywordScores.items():
            keywordScores[keyword] = score/(len(parties)-1)
            keywordFile.write(keyword)
            keywordFile.write("\n")
        keywordFile.close()
