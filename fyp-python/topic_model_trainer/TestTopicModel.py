topic_model_path = "assets/model-updated/topic_model.pkl"
vectorizer_path = "assets/model-updated/vectorizer.pkl"

try:
    topic_model = cPickle.load(open(topic_model_path, 'rb'))
except:
    print("Model: " + topic_model_path + " not found")
    exit(0)

try:
    vectorizer = cPickle.load(open(vectorizer_path, "rb"))
except:
    print("Vectorizer: " + vectorizer_path + " not found")
    exit(0)

# Model predicts numerous probabilities
# User has labelled with most likely topic, which is converted to number (1-14 - topic index)
# If model.predict yields true for this topic, get predict_proba for this
# If false, score of 0 is given
# Score is given based on predict_proba score - best is 1
# If all the topics are low scorers for a given article, if the user guesses it, they get a 1
# But, if there's some that are 1, and the user labels it as the main topic, the score is lowered
#   This is because the model hasn't predicted the best topic accurately, but still noted the topic's usage
# Keep to 1 decimal place, round up - clearer that way