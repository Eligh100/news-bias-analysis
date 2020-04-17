import re
import unicodedata
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize

class TextPreprocessor: 
    """Preprocess text using various NLP techniques"""

    def __init__(self):
        self.porterStemmer = PorterStemmer()
        self.lemmatizer = WordNetLemmatizer()

        self.stopWords = stopwords.words('english')

    def changeToLower(self, text):
        """Converts all text to lowercase
        
        Arguments:
            text {string} -- Text to be converted
        
        Returns:
            {string} -- Converted text
        """

        return text.lower()

    def replaceNewline(self, text, replacementChar):
        """Replaces all new-line characters to another chosen character
        
        Arguments:
            text {string} -- Text to be converted
            replacementChar {char} -- Character that will replace new-line character
        
        Returns:
            {string} -- Converted text
        """

        return text.replace("\n", replacementChar)

    def removeSpecialChars(self, text):
        """Removes all special characters from text (anything except letters)
        
        Arguments:
            text {string} -- Text to be converted
        
        Returns:
            {string} -- Converted text
        """

        return re.sub(r'[^a-zA-Z ]+', '', text)

    def stripAccents(self, text):
        """Strips accents from text, and replace with base unicode characters
        
        Arguments:
            text {string} -- Text to be converted
        
        Returns:
            {string} -- Converted text
        """

        return unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode("utf-8")

    def tokenizeWords(self, text):
        """Tokenizes (i.e. split) text into individual words
        
        Arguments:
            text {string} -- Text to be tokenized
        
        Returns:
            {[string]} -- List of tokenized words
        """

        return word_tokenize(text) 
    
    def tokenizeSentences(self, text): 
        """Tokenizes (i.e. split) text into individual sentences
        
        Arguments:
            text {string} -- Text to be tokenized
        
        Returns:
            {[string]} -- List of tokenized sentences
        """

        return sent_tokenize(text)

    def removeStopWords(self, text):
        """Removes stop words (i.e. 'and', 'the', etc.) from text
        
        Arguments:
            text {string} -- Text to be converted
        
        Returns:
            {string} -- Converted text
        """

        for stopword in self.stopWords:
            text = re.sub(rf' {stopword} ', ' ', text)
        return text

    def stemText(self, words):
        """Stems text using a porter stemmer
        
        Arguments:
            words {[string]} -- List of words to be stemmed
        
        Returns:
            {string} -- Stemmed text
        """

        stemmedText = ""
        for w in words:
            stemmedText += self.porterStemmer.stem(w) + " "

        return stemmedText

    def lemmatizeText(self, words): 
        """Lemmatizes text using a lemmatizer
        
        Arguments:
            words {[string]} -- List of words to be lemmatized
        
        Returns:
            {string} -- Lemmatized text
        """

        lemmatizedText = ""
        for w in words:
            lemmatizedText += self.lemmatizer.lemmatize(w) + " "
            
        return lemmatizedText

    def useOriginalWords(self, words):
        """Joins list of words together
        
        Arguments:
            words {[string]} -- List of words to be joined
        
        Returns:
            {string} -- Joined text
        """

        return " ".join(words)