# Get chunk of articles from 25/02/2020
# Then, uniform distribution of other dates
# Then, from these remaining table items, get equal mixture of organisations (Telegraph will be under-represented, no way around this)
# Then, download all matching items
# Feed into model, as different docs
# Throw in manifestos too
# Training/Test split
# Optimise model
# Select topics
# Save model, and use for topic selection

'''
We want 2000 articles total (1600 training, 400 testing - i.e. an 80/20 split)
Due to paywall-related problems, Telegraph only has 111 items, so they'll all be in
We can remove 89 from training (80% of 111) and 22 from testing (20% of 111)
So, 1889 articles (minus telegraph), with 1511 training articles and 378 testing articles
We want a good span over time, and a roughly even distribution of the other news organisations
Since lots of old data (pre-election to early post-election) was collected on the 25/02/2020, more will be collected from them, as this represents a two-month period
Half the data will be collected from this date
The other half will be an even distribution from each week, from week 07/01/2020 - 24/02/2020
i.e. 945 articles from 25/02/2020, and the remaining 944 over 7 weeks, or 944/7 =~ 135 a week
In all of this, the article orgs will be split equally

'''

import boto3
import re
from datetime import datetime

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

model_data_urls = set([])
extra_urls = set([])

MAX_EARLY = 945
MAX_LATE = 135
MAX_TELEGRAPH = 111

max_min_dates = {
    "7-14": [datetime(2020, 1, 7), datetime(2020, 1, 14)],
    "15-21": [datetime(2020, 1, 15), datetime(2020, 1, 21)],
    "22-28": [datetime(2020, 1, 22), datetime(2020, 1, 28)],
    "29-4": [datetime(2020, 1, 29), datetime(2020, 2, 4)],
    "5-11": [datetime(2020, 2, 5), datetime(2020, 2, 11)],
    "12-18": [datetime(2020, 2, 12), datetime(2020, 2, 18)],
    "19-24": [datetime(2020, 2, 19), datetime(2020, 2, 24)]
}

nov_to_early_jan_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

jan_7_to_jan_14_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

jan_15_to_jan_21_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

jan_22_to_jan_28_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

jan_29_to_feb_4_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

feb_5_to_feb_11_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

feb_12_to_feb_18_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

feb_19_to_feb_24_count = {
    "BBC": 0,
    "DAILY MAIL": 0,
    "INDEPENDENT": 0,
    "MIRROR": 0,
    "GUARDIAN": 0
}

converter = {
    "7-14": jan_7_to_jan_14_count,
    "15-21": jan_15_to_jan_21_count,
    "22-28": jan_22_to_jan_28_count,
    "29-4": jan_29_to_feb_4_count,
    "5-11": feb_5_to_feb_11_count,
    "12-18": feb_12_to_feb_18_count,
    "19-24": feb_19_to_feb_24_count
}

num_of_telegraph = 0

table = dynamodb.Table('Articles-Table')

results = table.scan()

for item in results["Items"]:
    if (len(model_data_urls) == 2000): # stop when all articles for model retrieved
        break

    if (item['article-org'] == "TELEGRAPH"): # add all telegraph articles, due to low number
        model_data_urls.add(item['article-url'])
        num_of_telegraph += 1
        continue
    
    if (item['article-org'] == "GUARDIAN" and "25/02/2020, 01" in (item['most-recent-update'])): # Get old guardian articles
        if (nov_to_early_jan_count[item['article-org']] != (MAX_EARLY / 5)):
            model_data_urls.add(item['article-url'])
            nov_to_early_jan_count[item['article-org']] += 1
            continue

    if (item['article-org'] != "GUARDIAN" and "25/02/2020, 13" in (item['most-recent-update'])): # Get old articles from other news orgs
        if (nov_to_early_jan_count[item['article-org']] != (MAX_EARLY / 5)):
            model_data_urls.add(item['article-url'])
            nov_to_early_jan_count[item['article-org']] += 1
            continue

    # if not an old article, ensure even mix of articles from each week
    article_date_time = datetime.strptime(item['most-recent-update'], "%d/%m/%Y, %H:%M:%S")

    for week_id, weeks in max_min_dates.items():
        if (article_date_time >= weeks[0] and article_date_time <= weeks[1]): # if article's date is in a certain week
            if (converter[week_id][item['article-org']] != (MAX_LATE / 5)):
                model_data_urls.add(item['article-url'])
                converter[week_id][item['article-org']] += 1
                break
            else:
                break

    # if it reaches here, then no criteria were met for the article
    # here, we should check if the max articles have been found
    # in theory, duplicate articles could have tried to be added, and failed
    # in this case, we just add the article found, otherwise the loop could end with less than 2000 articles
    # BUT, only if we have found every telegraph article!!
    if (num_of_telegraph >= MAX_TELEGRAPH):
        if (len(model_data_urls) < 2000):
            model_data_urls.add(item['article-url'])
    else:
        extra_urls.add(item['article-url'])

while(len(model_data_urls) != 2000):
    if (len(extra_urls) == 0):
        break
    model_data_urls.add(extra_urls.pop())

# Now, we have a list of 2000 articles urls for training/testing our models
# Next, we must save the S3 objects (containing the articles text) into assets/model_data
for item in results["Items"]:
    if item['article-url'] in model_data_urls:
        s3_object_url = item['article-text']
        # Download article text and save as .txt
        s3_object_filename = (s3_object_url.split("amazonaws.com/"))[1]
        # Get rid of anything after .txt
        trimmed = s3_object_filename.split(".txt")[0] + ".txt"
        trimmed = re.sub(r'[/\\:*?"<>|]', '', trimmed)
        local_filename = 'assets/model_data/' + trimmed
        s3.Bucket(bucket_name).download_file(s3_object_filename, local_filename)

'''
FINAL RESULTS:
    Since the database isn't equally weighted (i.e. more of some organisations than others), the final results weren't equally weighted
    The data consists of:
        Total: 2000 articles
        BBC: 323 articles
        Daily Mail: 238 articles
        Mirror: 404 articles
        Independent: 393 articles
        Guardian: 592 articles
        Telegraph: 50 articles
    So, we want train/test split of 90%/10%, meaning:
        Total: 1800 tr, 400 te
        BBC: 291 tr, 32 te
        Daily Mail: 214 tr, 24 te
        Mirror: 364 tr, 40 te
        Independent: 354 tr, 39 te
        Guardian: 534 tr, 60 te
        Telegraph: 45 tr, 5 te
'''