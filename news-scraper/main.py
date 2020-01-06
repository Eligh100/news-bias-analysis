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
#articleUploader = ArticleUploader()
#articleUploader.uploadArticles(database_entry)


'''
Look at chronjob (Linux) for script running on servers
Basic sentiment analysis on articles?
Log errors (need to check if script has been failing, and why)
'''