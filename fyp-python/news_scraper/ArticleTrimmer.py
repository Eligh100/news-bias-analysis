import urllib3
import certifi
import requests
from bs4 import BeautifulSoup
from bs4.element import Comment
from datetime import datetime

class ArticleTrimmer():
    """Extracts relevant information from the article, such as the main text, headline, authors, etc.
    
    Arguments:
        logger {Logger} -- Logger object, for logging exceptions
    """

    database_entry = {}

    org_headline_styles = {
        "BBC": "og:title",
        "DAILY MAIL": "mol:headline",
        "GUARDIAN": "og:title",
        "INDEPENDENT": "og:title",
        "TELEGRAPH": "og:title",
        "MIRROR": "og:title"
    }

    org_author_styles = {
        "DAILY MAIL": "author",
        "GUARDIAN": "author",
        "INDEPENDENT": "article:author_name",
        "TELEGRAPH": "DCSext.author",
        "MIRROR": "author"
    }

    additional_org_author_styles = {
        "GUARDIAN" : [["property", "article:author"]]
    }

    org_body_styles = {
        "BBC": ["class", "story-body"],
        "DAILY MAIL": ["itemprop", "articleBody"],
        "GUARDIAN": ["itemprop", "articleBody"],
        "INDEPENDENT": ["class", "body-content"],
        "TELEGRAPH": ["itemprop", "articleBody"],
        "MIRROR": ["itemprop", "articleBody"]
    }

    news_org_pub_date = {
        "BBC": ["div", "class", "date date--v2"], # Get first one, and get text
        "DAILY MAIL": ["meta", "property", "article:published_time"], # get content
        "TELEGRAPH": ["meta", "itemprop", "datePublished"], # Get first one, and get ["content"],
        "GUARDIAN": ["meta", "property", "article:published_time"], # Get content
        "INDEPENDENT": ["meta", "property", "article:published_time"], # get content
        "MIRROR": ["meta", "property","article:published_time"] # get content
    }

    org_body_containers = ["div", "article"]

    daily_mail_valid_article_words = ["political", "whitehall"]

    def __init__(self, logger):
        self.logger = logger

    def trimArticle(self, articles):
        """Extracts relevant information from the article
        
        Arguments:
            articles {dict} -- Dictionary received from NewsScraper.py
                Containing key: news organisation and value: list of URLs
        
        Returns:
            {dict(string, [])} -- Dictionary of key: article URL and value: list of article's information
                    Info is article text, headline, author, news organisation, and publish date
        """

        for org_name, article_links_list in articles.items():
                for article_url in article_links_list:
                    try:
                         response = urllib3.PoolManager(
                             cert_reqs='CERT_REQUIRED',
                             ca_certs=certifi.where()
                         ).request('GET', article_url)
                    except Exception as e:
                        try:
                            response = requests.get(article_url) # try using requests
                        except:
                            log_line = "Link failed - check url validity: " + article_url
                            log_line += "\nFailed with following exception:\n"
                            log_line += str(e)
                            self.logger.writeToLog(log_line, False)
                            continue
                    try:
                        soup = BeautifulSoup(response.data, 'html.parser')
                    except:
                        try:
                            soup = BeautifulSoup(response.text, 'html.parser') # requests uses 'text' instead of 'data'
                        except:
                            log_line = "Soup-ing failed - is URL xml: " + article_url
                            log_line += "\nFailed with the folowing exception:\n"
                            log_line += str(e)
                            self.logger.writeToLog(log_line, False)
                            continue

                    # If dailymail, ensure article is relevant (due to DailyMail's failure to tag articles accurately)
                    if (org_name == "DAILY MAIL ALL"):
                        article_author_details = soup.find_all("p", {"class":"author-section"})

                        valid_article = False
                        for article_author_detail in article_author_details:
                            try:
                                author_and_role = (article_author_detail.getText()).lower()
                            except:
                                continue
                            for validation_word in self.daily_mail_valid_article_words:
                                if (validation_word in author_and_role):
                                    valid_article = True
                                    break
                        
                        if (not valid_article):
                            continue
                        
                        org_name = "DAILY MAIL" # store with other daily mail articles

                    # Retrieve article's headline
                    article_headline = "NO_HEADLINE"

                    headlines = soup.find_all("meta", {"property":self.org_headline_styles[org_name]})
                    for headline in headlines:
                        try:
                            article_headline = headline["content"]
                        except:
                            article_headline = "NO_HEADLINE"

                    # Retrieve article's author
                    article_author = ""

                    if (org_name == "BBC"):
                        article_author = "BBC"
                    else:
                        authors = soup.find_all("meta", {"name":self.org_author_styles[org_name]})
                        for author in authors:
                            try:
                                article_author += author["content"] + ", "
                            except: # sometimes no author, just use org_name
                                article_author += org_name + ", "
                        article_author = article_author[:-2]
                        
                        if (article_author == ""):
                            try:
                                for additional_style in self.additional_org_author_styles[org_name]:
                                    authors = soup.find_all("meta", {additional_style[0]:additional_style[1]})
                                    for author in authors:
                                        article_author += author["content"] + ", "
                                    article_author = article_author[:-2]
                                    if (article_author == ""):
                                        continue
                                    else:
                                        break

                                if (article_author == ""):
                                    article_author = org_name # if no author found, set to news orgs name (i.e. GUARDIAN)
                            except:
                                article_author = org_name # if no author found, set to news orgs name (i.e. GUARDIAN)

                    # Retrieve article's publish date
                    article_pub_date = ""

                    pub_dates = soup.find_all(self.news_org_pub_date[org_name][0], {self.news_org_pub_date[org_name][1]:self.news_org_pub_date[org_name][2]})

                    for pub_date in pub_dates:
                    
                        if (org_name == "BBC"):
                            article_pub_date = pub_date.getText()
                            break
                        elif (org_name == "TELEGRAPH"):
                            try:
                                article_pub_date = pub_date["datetime"]
                            except:
                                try:
                                    article_pub_date = pub_date["content"]
                                except:
                                    continue
                                else:
                                    break
                            else:
                                break
                        else:
                            article_pub_date = pub_date["content"]
                            break
                    
                    if (org_name != "BBC"):
                        try:
                            article_pub_date = datetime.strptime(article_pub_date.split("T")[0], "%Y-%m-%d")
                        except Exception as e:
                            log_line = "Failed to save article's publishing date: " + article_url
                            log_line += "\nFailed with the folowing exception:\n"
                            log_line += str(e)
                            self.logger.writeToLog(log_line, False)
                        else:
                            article_pub_date = datetime.strftime(article_pub_date, "%d %B %Y")
                    
                    if article_pub_date == "":
                        article_pub_date = "NO INFO"

                    # Retrieve article's contents
                    for org_body_container in self.org_body_containers:
                        story_div = soup.find_all(org_body_container, {self.org_body_styles[org_name][0]:self.org_body_styles[org_name][1]})

                        article_text = ""

                        for story in story_div:

                            paragraphs_list = story.find_all("p")

                            for paragraph in paragraphs_list:
                                article_text += paragraph.getText() + "\n"
                        
                        if (article_text != ""):
                            break

                    if (article_text == ""):
                        log_line = "No  content found in: " + article_url
                        self.logger.writeToLog(log_line, False)

                        continue # don't bother adding article's with no text to DB (usually means error anyway)
                        
                    # Add the article and metadata to database dictionary
                    self.database_entry[article_url] = [article_text, article_headline, article_author, org_name, article_pub_date]
            
        return self.database_entry

