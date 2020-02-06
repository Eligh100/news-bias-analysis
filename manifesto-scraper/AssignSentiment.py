'''
Let's use textblob and analyse with the polarity score - perhaps subjectivity score will come in handy later?
'''

# TODO consider textblob's subjectivity

import os
import re
from textblob import TextBlob
from nltk import sent_tokenize

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

for manifesto in os.listdir('manifestos'):
    manifestoFilePath = "manifestos/" + manifesto
    partyName = manifesto[:-4]
    with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
        text = manifestoText.read()
        text = text.replace("\n", " ")

        manifestoSentences[partyName] = sent_tokenize(text)

for party,sentences in manifestoSentences.items():
    for sentence in sentences:
        sentencePolarity = TextBlob(sentence).sentiment.polarity
        if (abs(sentencePolarity) >= 0.5):
            polarisedSentences[party][sentence] = sentencePolarity


print(polarisedSentences)

        


