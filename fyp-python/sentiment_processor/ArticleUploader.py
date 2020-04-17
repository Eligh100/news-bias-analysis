import os
import boto3
from datetime import datetime

from helper_classes.Enums import PoliticalPartyHelper, TopicsHelper

class ArticleUploader():
    """Uploads article text to S3, and stores information/S3 URL in DynamoDB
        
    Arguments:
        s3 {Object} -- S3 instance
        bucket_name {string} -- Name of S3 bucket (file storage) where article text is stored
        table {Object} -- DynamoDB table where article information will be stored
        logger {Logger} -- Logger instance, for logging exceptions
        likely_topics {[int]} -- List of topic indexes
        likely_parties {[int]} -- List of party indexes
        article_topic_sentiment_matrix {dict{int:float}} -- Matrix of topic index -> sentiment scores from article
        article_party_sentiment_matrix {dict{int:float}} -- Matrix of party index -> sentiment scores from article
        most_similar_party {PoliticalParty} -- Enum of political party that text is most similar to
        headline_topics_sentiment_matrix {dict{int:float}} -- Matrix of topic index -> sentiment scores from headline
        headline_parties_sentiment_matrix {dict{int:float}} -- Matrix of party index -> sentiment scores from headline
        top_words {dict{word:float}} -- Matrix of word -> frequency score
    """

    def __init__(self, s3, bucket_name, table, logger, likely_topics, likely_parties, article_topic_sentiment_matrix, article_party_sentiment_matrix, most_similar_party, headline_topics_sentiment_matrix, headline_parties_sentiment_matrix, top_words):
        self.s3 = s3
        self.bucket_name = bucket_name
        self.table = table
        self.logger = logger

        self.likely_topics = likely_topics
        self.likely_parties = likely_parties
        self.article_topic_sentiment_matrix = article_topic_sentiment_matrix
        self.article_party_sentiment_matrix = article_party_sentiment_matrix
        self.most_similar_party = most_similar_party
        self.headline_topics_sentiment_matrix = headline_topics_sentiment_matrix
        self.headline_parties_sentiment_matrix = headline_parties_sentiment_matrix
        self.top_words = top_words

        self.tempUploadPath = "temp_files/tempUpload.txt"


    def uploadArticles(self, article_url, article_data):
        """Upload article text and information to S3/DynamoDB, for use by the website
        
        Arguments:
            article_url {string} -- URL of current article (used to uniquely index in S3/DynamoDB)
            article_data {[]} -- List of content/metadata about the article (text, headline, author, etc.)
        """

        # Store article text in S3 and get URL
        s3_url = ""
        if (article_data[0] != ""):
            # Open temp text file for uploading article contents to S3
            with open(self.tempUploadPath, "w", encoding="utf-8") as temp_text_file:
                # Write current article text to temp file
                try:
                    temp_text_file.truncate(0) # clear contents of file 
                    temp_text_file.write(article_data[0])
                    temp_text_file.close()
                except Exception as e:
                    log_line = "Writing to temp file: " + self.tempUploadPath + " failed\nThe following exception occured:\n" + str(e)
                    self.logger.writeToLog(log_line, False)
                else:
                    # Upload current article text to S3 and get URL
                    try:
                        article_url_sanitised = self.sanitiseURL(article_url)
                        self.s3.Bucket(self.bucket_name).upload_file(self.tempUploadPath, article_url_sanitised)
                        s3_url = self.getS3Url(article_url_sanitised)
                    except Exception as e:
                        log_line = "Uploading to S3 bucket failed\nThe following exception occured:\n" + str(e)
                        self.logger.writeToLog(log_line, False)

                if (s3_url != ""):
                    self.encodeDataToString()
                    self.updateDatabase(article_url, article_data, s3_url)

    def sanitiseURL(self, article_url):
        """Removes illegal characters from URL for storage in S3
        
        Arguments:
            article_url {string} -- URL to be sanitised
        
        Returns:
            {string} -- Sanitised URL
        """

        article_url = article_url.replace("http://","")
        article_url = article_url.replace("https://","")
        article_url = article_url.replace('/','FYPSLASHFYP')
        article_url += ".txt"
        return article_url

    def getS3Url(self, sanitised_url):
        """Construct S3 object URL for storage in DynamoDB (to connect the two storage solutions)
        
        Arguments:
            sanitised_url {string} -- URL of current article
        
        Returns:
            {string} -- S3 object URL, that points to object in S3 bucket
        """

        try:
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=self.bucket_name)
        except Exception as e:
            log_line = "Failed to locate bucket: " + self.bucket_name
            log_line += "\nFailed with the folowing exception:\n"
            log_line += str(e)
            log_line += "\nScript exited prematurely - "
            self.logger.writeToLog(log_line, True)
            exit(0)
            
        s3_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(
                self.bucket_name,
                bucket_location['LocationConstraint'],
                sanitised_url
        )
        return s3_url

    def encodeDataToString(self):
        """Encodes analysis data to strings for storage in DynamoDB (i.e. party_index of 1 becomes 'Labour')"""

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

        # If any data is empty, set to 'NO INFO' string - issues caused with empty fields in DynamoDB
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

    def updateDatabase(self, article_url, article_data, s3_url):       
        """Uploads/updates DynamoDB table with current article
        
        Arguments:
            article_url {string} -- URL of current article (used to uniquely index in S3/DynamoDB)
            article_data {[]} -- List of content/metadata about the article (text, headline, author, etc.)
            s3_url {string} -- S3 object URL, to locate text in bucket (stored with rest of attributes in DynamoDB)
        """

        now = datetime.now() # current date and time
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        try:
            response = self.table.get_item(
                Key={
                    'article-url': article_url,
                }
            )
        except Exception as e: # Should only fail if table can't be accessed
            log_line = "Failed to access DynamoDB table: Articles-Table\nThe following exception occured:\n" + str(e)
            self.logger.writeToLog(log_line, False)
            log_line = "Exited prematurely at: "
            self.logger.writeToLog(log_line, True)
            exit(0)
        else: 
            try:
                item = response["Item"]
            except: # if article doesn't exist, new entry in database
                try:
                    response = self.table.put_item(
                        Item={
                            'article-url': article_url,
                            'article-text': s3_url,
                            'article-headline': article_data[1],
                            'article-org': article_data[3], 
                            'article-author': article_data[2],
                            'most-recent-update': date_time,
                            'article-pub-date': article_data[4],
                            'article-topics': self.likely_topics,
                            "article-parties": self.likely_parties,
                            "article-topic-sentiments": self.article_topic_sentiment_matrix,
                            "article-party-sentiments": self.article_party_sentiment_matrix,
                            "most-likely-party": self.most_similar_party,
                            "headline-topic-sentiments": self.headline_topics_sentiment_matrix,
                            "headline-party-sentiments": self.headline_parties_sentiment_matrix,
                            "top-words": self.top_words 
                        }
                    )
                except:
                    log_line = "Failed to put item in DynamoDB database with following attributes:\n" + article_url + "\n" + s3_url + "\n" + article_data[1] + "\n" + article_data[3] + "\n" + article_data[2] + "\n" + date_time + "\nThe following exception occured:\n" + str(e)
                    self.logger.writeToLog(log_line, False)

            else: # if article exists, need to update entry in database (by default, file overwriting enabled in s3)
                response = self.table.update_item( # update database entry with new text and metadata
                    Key={
                        'article-url': article_url
                    },
                    ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                        "#at":"article-text",
                        "#aa":"article-author",
                        "#mru":"most-recent-update",
                        "#ah":"article-headline",
                        "#ao":"article-org",
                        "#apd":"article-pub-date",
                        "#atp":"article-topics",
                        "#apr":"article-parties",
                        "#ats":"article-topic-sentiments",
                        "#aps":"article-party-sentiments",
                        "#mlp":"most-likely-party",
                        "#hts":"headline-topic-sentiments",
                        "#hps":"headline-party-sentiments",
                        "#tw":"top-words"
                    },
                    UpdateExpression="SET #at=:t, #aa=:a, #mru=:u, #ah=:h, #ao=:o, #apd=:p, #atp=:b, #apr=:r, #ats=:s, #aps=:q, #mlp=:m, #hts=:f, #hps=:z, #tw=:w",
                    ExpressionAttributeValues={
                        ':t': s3_url,
                        ':a': article_data[2],
                        ':u': date_time,
                        ':h': article_data[1],
                        ':o': article_data[3],
                        ':p': article_data[4],
                        ':b': self.likely_topics,
                        ':r': self.likely_parties,
                        ':s': self.article_topic_sentiment_matrix,
                        ':q': self.article_party_sentiment_matrix,
                        ':m': self.most_similar_party,
                        ':f': self.headline_topics_sentiment_matrix,
                        ':z': self.headline_parties_sentiment_matrix,
                        ':w': self.top_words
                    },
                    ReturnValues="UPDATED_NEW"
                )
