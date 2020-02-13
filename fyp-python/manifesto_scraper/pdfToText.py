from tika import parser
import os

for manifestoPDF in os.listdir('manifestosPDF'):
    raw = parser.from_file("manifestosPDF/" + manifestoPDF)
    
    manifestoFileName = "manifestos/" + manifestoPDF[:-4] + ".txt"
    
    with open(manifestoFileName, "w", encoding="utf-8") as manifestoText:
        manifestoText.write(raw['content'])
        manifestoText.close()
    