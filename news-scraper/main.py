from NewsScraper import NewsScraper
from ArticleTrimmer import ArticleTrimmer
from ArticleUploader import ArticleUploader

# Get articles
newsScraper = NewsScraper()
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer()
database_entry = articleTrimmer.trimArticle(articles)

# Upload articles and relevant metadata to S3 and DynamoDB
articleUploader = ArticleUploader()
articleUploader.uploadArticles(database_entry)


'''
Look at chronjob (Linux) for script running on servers
Working script that grabs articles and stores in database
Diagrams to demonstrate usage of system
Basic sentiment analysis on articles?
Automation of script running 
    schedule lambda function?
'''