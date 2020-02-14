'''
I later chose to include article headlines and organisation names in my 'articles-table' DynamoDB database
This script posthumously updates items in the DynamoDB table to include this information
This script was ran once to add these features (and is not referenced elsewhere in the program)
Script can be amended to grab more features, if necessary, and ran again as needed
'''

import boto3
import re
import urllib3
import certifi
from bs4 import BeautifulSoup

# Establish AWS-related variables
bucket_name = "articles-text"
ACCESS_KEY_ID = "AKIASRO4ILWKGIB27HGU"
SECRET_ACCESS_KEY = "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"

s3 = boto3.resource(
    's3',
    aws_access_key_id = ACCESS_KEY_ID,
    aws_secret_access_key = SECRET_ACCESS_KEY
    )

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id = ACCESS_KEY_ID,
    aws_secret_access_key = SECRET_ACCESS_KEY
    )

org_headline_styles = {
    "BBC": "og:title",
    "DAILY MAIL": "mol:headline",
    "GUARDIAN": "og:title",
    "INDEPENDENT": "og:title",
    "TELEGRAPH": "og:title",
    "MIRROR": "og:title"
}

url_names = {
    "bbc": "BBC",
    "dailymail": "DAILY MAIL",
    "theguardian": "GUARDIAN",
    "independent": "INDEPENDENT",
    "telegraph": "TELEGRAPH",
    "mirror": "MIRROR"
}

table = dynamodb.Table('Articles-Table')

results = table.scan()

for item in results["Items"]:
    article_url = item['article-url']

    org_name = ""
    if (".bbc.co" in article_url):
        org_name = "BBC"
    elif (".dailymail.co" in article_url):
        org_name = "DAILY MAIL"
    elif (".theguardian.co" in article_url):
        org_name = "GUARDIAN"
    elif (".independent.co" in article_url):
        org_name = "INDEPENDENT"
    elif (".telegraph.co" in article_url):
        org_name = "TELEGRAPH"
    elif (".mirror.co" in article_url):
        org_name = "MIRROR"

    article_headline = "NO_HEADLINE"

    # Soup the URL
    try:
        response = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=certifi.where()
        ).request('GET', article_url)
    except Exception as e:
        print("Response failed: " + article_url)
    else:
        try:
            soup = BeautifulSoup(response.data, 'html.parser')
        except:
            print("Soup-ing failed: " + article_url)
        else:
            # Get headline
            headlines = soup.find_all("meta", {"property":org_headline_styles[org_name]})
            for headline in headlines:
                try:
                    article_headline = headline["content"]
                except:
                    article_headline = "NO_HEADLINE"

    response = table.update_item( # update database entry with headline and org name
                Key={
                    'article-url': article_url
                },
                ExpressionAttributeNames = { # necessary as "-" in column names cause issues
                    "#ah":"article-headline",
                    "#ao":"article-org"
                },
                UpdateExpression="SET #ah=:h, #ao=:o",
                ExpressionAttributeValues={
                    ':h': article_headline,
                    ':o': org_name
                },
                ReturnValues="UPDATED_NEW"
            )

