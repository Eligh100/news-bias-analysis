import re
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

class TextPreprocessor: 

    def __init__(self, logger):
        self.porterStemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.stopWords = stopwords.words('english')

        self.logger = logger

    def changeToLower(self, text):
        return text.lower()

    def replaceNewline(self, text, replacementChar):
        return text.replace("\n", replacementChar)

    def removeSpecialChars(self, text):
        return re.sub(r'[^a-zA-Z ]+', '', text)

    def stripAccents(self, text):
        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

    def tokenizeWords(self, text):
        return word_tokenize(text) 
    
    def tokenizeSentences(self, text): 
        return sent_tokenize(text)

    def removeStopWords(self, text): 
        for stopword in self.stopWords:
            text = re.sub(rf' {stopword} ', ' ', text)
        return text

    def stemText(self, words): 
        stemmedText = ""
        for w in words:
            stemmedText += self.porterStemmer.stem(w) + " "

        return stemmedText

    def lemmatizeText(self, words): 
        lemmatizedText = ""
        for w in words:
            lemmatizedText += self.lemmatizer.lemmatize(w) + " "
            
        return lemmatizedText

    def useOriginalWords(self, words):
        return " ".join(words)