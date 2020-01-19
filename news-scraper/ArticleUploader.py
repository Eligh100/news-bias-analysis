import os
import boto3
from datetime import datetime

from Logger import Logger

class ArticleUploader():

    database_additions = {}

    s3 = ""
    bucket_name = ""
    dynamodb = ""

    logger = ""

    def __init__(self, s3, bucket_name, dynamodb):
        self.s3 = s3
        self.bucket_name = bucket_name
        self.dynamodb = dynamodb
        self.logger = Logger()


    def uploadArticles(self, database_entry):
        # Store article text in S3 and get URL
        for article_url, article_data in database_entry.items():
            s3_url = ""
            if (article_data[0] != ""):
                # Open temp text file for uploading article contents to S3
                with open("temp.txt", "w", encoding="utf-8") as temp_text_file:
                    # Write current article text to temp file
                    try:
                        temp_text_file.truncate(0) # clear contents of file 
                        temp_text_file.write(article_data[0])
                        temp_text_file.close()
                    except Exception as e:
                        log_line = "Writing to temp file failed\nThe following exception occured:\n" + str(e)
                        self.logger.writeToLog(log_line, False)
                    else:
                        # Upload current article text to S3 and get URL
                        try:
                            article_url_sanitised = self.sanitiseURL(article_url)
                            self.s3.Bucket(self.bucket_name).upload_file("temp.txt", article_url_sanitised)
                            s3_url = self.getS3Url(article_url_sanitised)
                        except Exception as e:
                            log_line = "Uploading to S3 bucket failed\nThe following exception occured:\n" + str(e)
                            self.logger.writeToLog(log_line, False)

                    if (s3_url != ""):
                        self.updateDatabase(article_url, article_data, s3_url)

        # Delete temp text file
        try:
            os.remove("temp.txt")
        except OSError as e:
            log_line = "Couldn't delete temp text file\nThe following exception occured:\n" + str(e) 
            self.logger.writeToLog(log_line, False)

    def sanitiseURL(self, article_url):
        article_url = article_url.replace("http://","")
        article_url = article_url.replace("https://","")
        article_url = article_url.replace('/','FYPSLASHFYP')
        article_url += ".txt"
        return article_url

    def getS3Url(self, sanitised_url):
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=self.bucket_name)
        s3_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(
                self.bucket_name,
                bucket_location['LocationConstraint'],
                sanitised_url
        )
        return s3_url

    def updateDatabase(self, article_url, article_data, s3_url):
        table = self.dynamodb.Table('Articles-Table')
        
        now = datetime.now() # current date and time
        date_time = now.strftime("%d/%m/%Y, %H:%M:%S")

        try:
            response = table.get_item(
                Key={
                    'article-url': article_url,
                }
            )
        except Exception as e:
            log_line = "Failed to access DynamDB table: Articles-Table\nThe following exception occured:\n" + str(e)
            self.logger.writeToLog(log_line, False)
            log_line = "Exited prematurely at: "
            self.logger.writeToLog(log_line, True)
            exit(0)
        else: 
            try:
                item = response["Item"]
            except: # if article doesn't exist, new entry in database
                try:
                    response = table.put_item(
                        Item={
                            'article-url': article_url,
                            'article-text': s3_url,
                            'article-author': article_data[2],
                            'most-recent-update': date_time
                        }
                    )
                except:
                    print (article_url)
                    print (s3_url)
                    print (article_data[2])
                    print (date_time)

            else: # if article exists, need to update entry in database (by default, file overwriting enabled in s3)
                response = table.update_item( # update database entry with new text and metadata
                    Key={
                        'article-url': article_url
                    },
                    ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                        "#at":"article-text",
                        "#aa":"article-author",
                        "#mru":"most-recent-update"
                    },
                    UpdateExpression="SET #at=:t, #aa=:a, #mru=:u",
                    ExpressionAttributeValues={
                        ':t': s3_url,
                        ':a': article_data[2],
                        ':u': date_time
                    },
                    ReturnValues="UPDATED_NEW"
                )
