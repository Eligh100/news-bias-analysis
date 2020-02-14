import urllib3
import certifi
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests

class ArticleTrimmer():

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
        "BBC": ["div", "class", "story-body"],
        "DAILY MAIL": ["div", "itemprop", "articleBody"],
        "GUARDIAN": ["div", "itemprop", "articleBody"],
        "INDEPENDENT": ["div", "class", "body-content"],
        "TELEGRAPH": ["article", "itemprop", "articleBody"],
        "MIRROR": ["div", "itemprop", "articleBody"]
    }

    def __init__(self, logger):
        self.logger = logger

    def trimArticle(self, articles):
        for org_name, article_links_list in articles.items():
                for article_url in article_links_list:
                    try:
                         response = urllib3.PoolManager(
                             cert_reqs='CERT_REQUIRED',
                             ca_certs=certifi.where()
                         ).request('GET', article_url)
                    except Exception as e:
                        log_line = "Link failed - check url validity: " + article_url
                        log_line += "\nFailed with following exception:\n"
                        log_line += str(e)
                        self.logger.writeToLog(log_line, False)
                    else:
                        try:
                            soup = BeautifulSoup(response.data, 'html.parser')
                        except:
                            log_line = "Soup-ing failed - is URL xml: " + article_url
                            log_line += "\nFailed with the folowing exception:\n"
                            log_line += e
                            self.logger.writeToLog(log_line, False)
                        else:
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


                            # Retrieve article's contents
                            story_div = soup.find_all(self.org_body_styles[org_name][0], {self.org_body_styles[org_name][1]:self.org_body_styles[org_name][2]})

                            article_text = ""

                            for story in story_div:

                                paragraphs_list = story.find_all("p") # TODO get list items too?

                                for paragraph in paragraphs_list:
                                    article_text += paragraph.getText() + "\n"
                            
                            # Add the article and metadata to database dictionary
                            self.database_entry[article_url] = [article_text, article_headline, article_author, org_name]
                
                            
        return self.database_entry

    def tagVisible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

