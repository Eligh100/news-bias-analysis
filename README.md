# Quantifying and Visualsing Political Bias in News
Tool at https://uk-news-bias.web.app/      <<<------------------

TO ACCESS AWS:
  Account ID/Alias: eligh-fyp
  IAM Username: External1/External2
  Password: FYPViewServices2020

TO CONFIGURE PYTHON LIBRARIES:
  Use `conda env create -f environment.yml` in *fyp-python* directory to create the conda environment with the correct packages. 
  To install conda, visit https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html

TO RUN THE DAILY SCRIPT:
  run `main.py` from *fyp-python* directory
  
TO LOCALLY SERVE THE WEBSITE:
  run `ng serve` from *bias-analyser* directory
  
TO TRAIN AND TEST CLASSIFIER MODELS:
  See python files in *topic_model_trainer* directory
  run from *fyp-python* directory

For running unit tests (from *fyp-python* directory):

`python -m unittest testing/unit/test_ArticleAnalyser.py testing/unit/test_ArticleTrimmer.py testing/unit/test_ArticleUploader.py testing/unit/test_Logger.py testing/unit/test_NewsScraper.py testing/unit/test_TextPreprocessor.py`

For running unit tests with code coverage (from *fyp-python* directory):

`coverage run -m unittest testing/unit/test_ArticleAnalyser.py testing/unit/test_ArticleTrimmer.py testing/unit/test_ArticleUploader.py testing/unit/test_Logger.py testing/unit/test_NewsScraper.py testing/unit/test_TextPreprocessor.py`

Use `coverage report` to view results


