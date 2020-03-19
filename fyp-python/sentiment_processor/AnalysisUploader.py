from helper_classes.Enums import PoliticalPartyHelper, TopicsHelper

class AnalysisUploader:

    def __init__(self, logger, article_url, likely_topics, likely_parties, article_topic_sentiment_matrix, article_party_sentiment_matrix, most_similar_party, headline_topics_sentiment_matrix, headline_parties_sentiment_matrix, top_words):
        self.logger = logger
        self.article_url = article_url
        self.likely_topics = likely_topics
        self.likely_parties = likely_parties
        self.article_topic_sentiment_matrix = article_topic_sentiment_matrix
        self.article_party_sentiment_matrix = article_party_sentiment_matrix
        self.most_similar_party = most_similar_party
        self.headline_topics_sentiment_matrix = headline_topics_sentiment_matrix
        self.headline_parties_sentiment_matrix = headline_parties_sentiment_matrix
        self.top_words = top_words

    # Encode analysed article text data for database
    def encodeDataToString(self):
        self.likely_topics = ", ".join([TopicsHelper.topicIndexToTopic[likely_topic] for likely_topic in self.likely_topics if likely_topic != 0])

        self.likely_parties = ", ".join([PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[likely_party]] for likely_party in self.likely_parties if likely_party != 0])

        self.article_topic_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in self.article_topic_sentiment_matrix.items() if topic_num != 0])
        self.article_topic_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in self.article_topic_sentiment_matrix.items()])

        self.article_party_sentiment_matrix = dict([(PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[party_num]], party_sentiment) for party_num,party_sentiment in self.article_party_sentiment_matrix.items() if party_num != 0])
        self.article_party_sentiment_matrix = ", ".join([party + " = " + str(score) for party, score in self.article_party_sentiment_matrix.items()])

        self.most_similar_party = PoliticalPartyHelper.enumToPoliticalPartyString[self.most_similar_party]

        self.headline_topics_sentiment_matrix = dict([(TopicsHelper.topicIndexToTopic[topic_num], topic_sentiment) for topic_num,topic_sentiment in self.headline_topics_sentiment_matrix.items() if topic_num != 0])
        self.headline_topics_sentiment_matrix = ", ".join([topic + " = " + str(score) for topic, score in self.headline_topics_sentiment_matrix.items()])

        self.headline_parties_sentiment_matrix = dict([(PoliticalPartyHelper.enumToPoliticalPartyString[PoliticalPartyHelper.partyNumToEnum[party_num]], party_sentiment) for party_num,party_sentiment in self.headline_parties_sentiment_matrix.items() if party_num != 0])
        self.headline_parties_sentiment_matrix = ", ".join([party + " = " + str(score) for party, score in self.headline_parties_sentiment_matrix.items()])

        self.top_words = ", ".join([word + " = " + str(score) for word,score in self.top_words.items()])

        if (self.likely_topics == ""):
            self.likely_topics = "NO INFO"
        if (self.likely_parties == ""):
            self.likely_parties = "NO INFO"
        if (self.article_topic_sentiment_matrix == ""):
            self.article_topic_sentiment_matrix = "NO INFO"
        if (self.article_party_sentiment_matrix == ""):
            self.article_party_sentiment_matrix = "NO INFO"
        if (self.most_similar_party == ""):
            self.most_similar_party = "NO INFO"
        if (self.headline_topics_sentiment_matrix == ""):
            self.headline_topics_sentiment_matrix = "NO INFO"
        if (self.headline_parties_sentiment_matrix == ""):
            self.headline_parties_sentiment_matrix = "NO INFO"
        if (self.top_words == ""):
            self.top_words = "NO INFO"

    # Pushes analysis info to 'articles-table' in DynamoDB
    def pushAnalysis(self, table):
        response = table.update_item( # update database entry with new text and metadata
            Key={
                'article-url': self.article_url
            },
            ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                "#atp":"article-topics",
                "#apr":"article-parties",
                "#ats":"article-topic-sentiments",
                "#aps":"article-party-sentiments",
                "#mlp":"most-likely-party",
                "#hts":"headline-topic-sentiments",
                "#hps":"headline-party-sentiments",
                "#tw":"top-words"
            },
            UpdateExpression="SET #atp=:t, #apr=:r, #ats=:s, #aps=:q, #mlp=:m, #hts=:h, #hps=:z, #tw=:w",
            ExpressionAttributeValues={
                ':t': self.likely_topics,
                ':r': self.likely_parties,
                ':s': self.article_topic_sentiment_matrix,
                ':q': self.article_party_sentiment_matrix,
                ':m': self.most_similar_party,
                ':h': self.headline_topics_sentiment_matrix,
                ':z': self.headline_parties_sentiment_matrix,
                ':w': self.top_words,            
            },
            ReturnValues="UPDATED_NEW"
        )