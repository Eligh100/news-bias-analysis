'''
Let's use textblob and analyse with the polarity score - perhaps subjectivity score will come in handy later?
'''

# TODO consider textblob's subjectivity

import os
import re
from textblob import TextBlob
from nltk import sent_tokenize

from helper_classes.Logger import Logger
from helper_classes.TextPreprocessor import TextPreprocessor

manifestoSentences = {
    "BrexitParty": [],
    "Conservative": [],
    "Green": [],
    "Labour": [],
    "LibDem": [],
    "PlaidCymru": [],
    "SNP": [],
    "UKIP": []
}

polarisedSentences = {
    "BrexitParty": {},
    "Conservative": {},
    "Green": {},
    "Labour": {},
    "LibDem": {},
    "PlaidCymru": {},
    "SNP": {},
    "UKIP": {}
}

logger = Logger("manifesto_scraper/sentimentAssignerLog.txt")
preprocessor = TextPreprocessor(logger)

for manifesto in os.listdir('manifestos'):
    manifestoFilePath = "manifestos/" + manifesto
    partyName = manifesto[:-4]
    with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
        text = manifestoText.read()

        text = preprocessor.replaceNewline(text, ' ')
        manifestoSentences[partyName] = preprocessor.tokenizeSentences(text)

for party,sentences in manifestoSentences.items():
    with open("sentiment-sentences/" + party + "Sentiment.txt", "w", encoding="utf-8") as sentimentFile:
        for sentence in sentences:
            sentencePolarity = TextBlob(sentence).sentiment.polarity
            sentenceSubjectivity = TextBlob(sentence).sentiment.subjectivity
            if (abs(sentencePolarity) >= 0.5 and sentenceSubjectivity >= 0.5):
                polarisedSentences[party][sentence] = sentencePolarity
                sentimentFile.write(sentence + " = " + str(sentencePolarity) + "\n")
        sentimentFile.close()
            




        


