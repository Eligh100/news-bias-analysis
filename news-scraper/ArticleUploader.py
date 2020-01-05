import os
import boto3

class ArticleUploader():

    # Establish S3-related variables
    bucket_name = "articles-text"
    ACCESS_KEY_ID = "AKIASRO4ILWKGIB27HGU"
    SECRET_ACCESS_KEY = "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"

    s3 = boto3.resource(
        's3',
        aws_access_key_id = ACCESS_KEY_ID,
        aws_secret_access_key = SECRET_ACCESS_KEY
        )

    def uploadArticles(self, database_entry):
        # Store article text in S3 and get URL
        for article_url, article_data in database_entry.items():
            if (article_data[0] != ""):
                # Open temp text file for uploading article contents to S3
                try:
                    temp_text_file = open("temp.txt", "w")
                except:
                    print("Failed to create temp file")
                    exit(0)
                else:
                    # Write current article text to temp file
                    try:
                        temp_text_file.truncate(0) # clear contents of file 
                        temp_text_file.write(article_data[0])
                        temp_text_file.close()
                    except:
                        print("Writing to temp file failed")
                    else:
                        # Upload current article text to S3 and get URL
                        try:
                            article_url_sanitised = self.sanitiseURL(article_url)
                            self.s3.Bucket(self.bucket_name).upload_file("temp.txt", article_url_sanitised)
                            s3_url = self.getS3Url(article_url_sanitised)
                            print(s3_url)
                        except Exception as e:
                            print("Uploading to S3 bucket failed: ")
                            print(e)

        # Delete temp text file
        try:
            os.remove("temp.txt")
        except OSError:
            pass

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
