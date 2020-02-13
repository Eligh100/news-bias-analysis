import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

class ArticlePreProcessor:

    def __init__(self):
        self.porterStemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.stopWords = stopwords.words('english')

    def preprocess(self, text):
        text = text.lower() # TODO improve this - entity resolution?
        text = re.sub(r'[^a-zA-Z ]+', '', text) # TODO is this best option?
        words = word_tokenize(text) # TODO better tokenizer? and sentence tokenizer?
        words = [word for word in words if word not in self.stopWords] # TODO bespoke stopword list? with party names in, for instance

        lemmatizedText = ""
        for w in words:
            lemmatizedText += self.lemmatizer.lemmatize(w) + " "

        words = " ".join(words)

        return words
    