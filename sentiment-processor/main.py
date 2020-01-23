from ArticlePreProcessor import ArticlePreProcessor

'''
for each article in dynamodb database (in time range - default is ALL)
retrieve article table entry
put s3 link through article preprocessor
'''

# Read in articles, and do pre-processing for each one (tokinisation)
articlePreProcessor = ArticlePreProcessor()
