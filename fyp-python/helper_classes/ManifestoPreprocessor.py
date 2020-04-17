import os
from helper_classes.TextPreprocessor import TextPreprocessor

preprocessor = TextPreprocessor()

# For each manifesto, preprocess it's text, and upload as new file
for manifesto in os.listdir('manifesto_scraper/manifestos'):
    manifestoFilePath = "manifesto_scraper/manifestos/" + manifesto
    with open(manifestoFilePath , "r", encoding="utf-8") as manifestoText:
        text = manifestoText.read()

        # Preprocess the manifesto's text
        text = preprocessor.changeToLower(text)
        text = preprocessor.replaceNewline(text, ' ')
        text = preprocessor.removeStopWords(text)
        text = preprocessor.stripAccents(text)
        text = preprocessor.removeSpecialChars(text)
        words = preprocessor.tokenizeWords(text)

        preprocessed_text = preprocessor.useOriginalWords(words)

        # Upload processed manifesto
        manifestoName = manifesto[:-4]
        manifestoProcessedPath = "manifesto_scraper/manifestosProcessed/" + manifestoName +  "Processed.txt"
        with open(manifestoProcessedPath, "w", encoding="utf-8") as manifestoProcessedFile:
            manifestoProcessedFile.write(preprocessed_text)
            manifestoProcessedFile.close()