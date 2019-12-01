from NewsScraper import NewsScraper
from ArticleTrimmer import ArticleTrimmer

# Get articles
newsScraper = NewsScraper()
articles = newsScraper.scrapeArticles()

# Extract text
articleTrimmer = ArticleTrimmer()
articleTrimmer.trimArticle(articles)

# Store in DB



'''
Look at chronjob (Linux) for script running on servers
For next Wednesday:
    Working script that grabs articles and stores in database
    Diagrams to demonstrate usage of system
    Basic sentiment analysis on articles?
    Automation of script running 
        schedule lambda function?
'''