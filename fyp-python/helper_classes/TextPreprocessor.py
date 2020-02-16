import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

class TextPreprocessor: # TODO add logging

    def __init__(self, logger):
        self.porterStemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.stopWords = stopwords.words('english')

        self.logger = logger

    def changeToLower(self, text): # TODO improve this - entity resolution?
        return text.lower()

    def replaceNewline(self, text, replacementChar):
        return text.replace("\n", replacementChar)

    def removeSpecialChars(self, text): # TODO improve this?
        return re.sub(r'[^a-zA-Z ]+', '', text)

    def tokenizeWords(self, text): # TODO better tokenizer?
        return word_tokenize(text) 
    
    def tokenizeSentences(self, text): # TODO better tokenizer?
        return sent_tokenize(text)

    def removeStopWords(self, words): # TODO bespoke/custom stopword list? with party names in, for instance
        return [word for word in words if word not in self.stopWords] 

    def stemText(self, words): # TODO better stemmer?
        stemmedText = ""
        for w in words:
            stemmedText += self.porterStemmer.stem(w) + " "

        return stemmedText

    def lemmatizeText(self, words): #TODO better lemmatizer?
        lemmatizedText = ""
        for w in words:
            lemmatizedText += self.lemmatizer.lemmatize(w) + " "

        return lemmatizedText

    def useOriginalWords(self, words):
        return " ".join(words)