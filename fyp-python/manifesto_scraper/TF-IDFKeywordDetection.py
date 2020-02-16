'''
This code uses TF-IDF to cross-reference all party manifestos, and select unique keywords
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

vectorizerParameters = [(1,2), (2,2), (3,3)] # This determines whether unigram, bigram, or trigram
fileOutputParameters = ["unibimix", "bigrams", "trigrams"]

userChoice = -1
while (userChoice not in [1, 2, 3]):
    try:
        userChoice = int(input("1 for unigrams, 2 for bigrams, or 3 for trigrams: "))
    except:
        print("Invalid input")

# TODO remove party name from text? i.e. labour is common word in labour manifesto, but not necessarily helpful?

# Get preprocessed manifesto text
manifestoTexts = []
for manifestoProcessed in os.listdir('manifesto_scraper/manifestosProcessed'):
    manifestoFilePath = "manifesto_scraper/manifestosProcessed/" + manifestoProcessed
    with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
        text = manifestoText.read()
        manifestoTexts.append(text)
        manifestoText.close()

# Vectorise, and get top 20 words, with highest TF-IDF score

keywords = {}

for i in range(0,len(parties)):
    keywords[i] = []
    for j in range(0,len(parties)):
        if (i != j):
            vectorizer = TfidfVectorizer(ngram_range=vectorizerParameters[userChoice-1])
            vectors = vectorizer.fit_transform([manifestoTexts[i], manifestoTexts[j]])
            feature_names = vectorizer.get_feature_names()
            dense = vectors.todense()
            denselist = dense.tolist()
            df = pd.DataFrame(denselist, columns=feature_names)
            top_words = df.iloc[[0]].sum(axis=0).sort_values(ascending=False)

            keywords[i].append(top_words[0:20])

# Accumulate scores of TF-IDF keywords that appear more than once (e.g. high scorer for M1 -> M2, and M1 -> M4)

totalScoresDict = {}

for partyIndex,partyKeywordList in keywords.items():
    partyName = parties[partyIndex]
    totalScoresDict[partyName] = {}
    for keywordsScoreDict in partyKeywordList:
        for currentKeyword,currentKeywordScore in keywordsScoreDict.items():
            if currentKeyword not in totalScoresDict[partyName]:
                totalScoresDict[partyName][currentKeyword] = 0.0
            totalScoresDict[partyName][currentKeyword] += currentKeywordScore

# Write to file
for party,keywordScores in totalScoresDict.items():
    keywordsFilePath = "manifesto_scraper/" + fileOutputParameters[userChoice-1] + "/" + party + "-" + fileOutputParameters[userChoice-1] + ".txt"
    with open(keywordsFilePath, "w", encoding="utf-8") as keywordFile:
        for keyword,score in keywordScores.items():
            keywordScores[keyword] = score/(len(parties)-1)
            textFileLine = keyword + " = "
            textFileLine += str(keywordScores[keyword])
            keywordFile.write(textFileLine)
            keywordFile.write("\n")
        keywordFile.close()

# Code for wordcloud
wc = WordCloud(background_color="white",width=1000,height=1000, max_words=50,relative_scaling=0.5,normalize_plurals=False).generate_from_frequencies(totalScoresDict["Green"])
plt.imshow(wc)
plt.show()

# TODO save these word clouds to DynamoDB table