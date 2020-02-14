class AnalysisUploader:

    def __init__(self, logger):
        self.logger = logger

    def pushAnalysis(self):
        print("") # TODO implement - pushes analysis info to 'articles-table' in DynamoDB