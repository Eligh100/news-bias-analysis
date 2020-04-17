from tika import parser
import os

# For each manifesto in PDF form, write raw text to text file
for manifestoPDF in os.listdir('manifesto_scraper/manifestosPDF'):
    raw = parser.from_file("manifesto_scraper/manifestosPDF/" + manifestoPDF)
    
    manifestoFileName = "manifesto_scraper/manifestos/" + manifestoPDF[:-4] + ".txt"
    
    with open(manifestoFileName, "w", encoding="utf-8") as manifestoText:
        manifestoText.write(raw['content'])
        manifestoText.close()
    