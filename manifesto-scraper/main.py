import os
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize 
import pandas as pd
import re


# first, gather text for each manifesto

manifestoTexts = []
porterStemmer = PorterStemmer()
lemmatizer = WordNetLemmatizer()

stopWords = stopwords.words('english')

# then, pre-process (remove stop words and stem)   WENZELS

for manifesto in os.listdir('manifestos'):
    manifestoFilePath = "manifestos/" + manifesto
    with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
        print(manifesto)
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
    for j in range(0,7):
        keywords[i] = []
        if (i != j):
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([manifestoTexts[i], manifestoTexts[j]])
            feature_names = vectorizer.get_feature_names()
            dense = vectors.todense()
            denselist = dense.tolist()
            df = pd.DataFrame(denselist, columns=feature_names)
            top_words = df.iloc[[0]].sum(axis=0).sort_values(ascending=False)

            keywords[i].append(top_words[0:20])

print (keywords)



# save to dynamodb database