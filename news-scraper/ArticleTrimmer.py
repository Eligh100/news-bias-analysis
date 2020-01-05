import urllib3
import certifi
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests

class ArticleTrimmer():

    database_entry = {}
    
    def trimArticle(self, articles):
        for org_name, article_links_list in articles.items():
            if (org_name == "BBC"):
                for article_url in article_links_list:
                    try:
                         response = urllib3.PoolManager(
                             cert_reqs='CERT_REQUIRED',
                             ca_certs=certifi.where()
                         ).request('GET', article_url)
                        #request = requests.get(article_url)
                        #html_page = request.content
                    except:
                        print("Link failed - check url validity: " + article_url)
                    else:
                        try:
                            soup = BeautifulSoup(response.data, 'html.parser')
                        except:
                            print("Soup-ing failed - is URL xml: " + article_url)
                        else:
                            story_div = soup.find_all("div", {"class": "story-body"})

                            for story in story_div:

                                if (org_name == "BBC"):
                                    article_author = "BBC"

                                paragraphs_list = story.find_all("p", text=True)

                                article_text = ""

                                for paragraph in paragraphs_list:
                                    article_text += paragraph.getText() + "\n"

                                # Add the article and metadata to database dictionary
                                self.database_entry[article_url] = [article_text, article_author]
                                
                            break
                return self.database_entry

    def tagVisible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

