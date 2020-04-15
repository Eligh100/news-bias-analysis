from sklearn.feature_extraction.text import CountVectorizer
import operator

# list of text documents
text = ["\"The NHS is struggling without funding, and the Tories need to do something\", says Jeremy Corbyn", "Boris Johnson says budget will have funding for \"struggling NHS\" and the North"]
# create the transform
vectorizer = CountVectorizer()
# tokenize and build vocab
vectorizer.fit(text)
# summarize
sorted_d = sorted(vectorizer.vocabulary_.items(), key=operator.itemgetter(1))
test1 = []

for i in sorted_d:
    test1.append(i[0])
print(test1)

# encode document
vector = vectorizer.transform(text)
# summarize encoded vector
print(vector.shape)
print(type(vector))
print(vector.toarray())

