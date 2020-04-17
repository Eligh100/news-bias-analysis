# FYP
Github repository for final year project

Tool at https://uk-news-bias.web.app/

Account ID/Alias: eligh-fyp

IAM Username: External1/External2

Password: FYPViewServices2020

For running unit tests (from *fyp-python* directory):

`python -m unittest testing/unit/test_ArticleAnalyser.py testing/unit/test_ArticleTrimmer.py testing/unit/test_ArticleUploader.py testing/unit/test_Logger.py testing/unit/test_NewsScraper.py testing/unit/test_TextPreprocessor.py`

For running unit tests with code coverage (from *fyp-python* directory):

`coverage run -m unittest testing/unit/test_ArticleAnalyser.py testing/unit/test_ArticleTrimmer.py testing/unit/test_ArticleUploader.py testing/unit/test_Logger.py testing/unit/test_NewsScraper.py testing/unit/test_TextPreprocessor.py`

Use `coverage report` to view results
