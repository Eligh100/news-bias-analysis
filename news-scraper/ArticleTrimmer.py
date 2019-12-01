import urllib3
import certifi
from bs4 import BeautifulSoup
from bs4.element import Comment
import requests

class ArticleTrimmer():
    
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

                                article_text = story.find_all("p", text=True)

                                for paragraph in article_text:
                                    print (paragraph.getText())

                                print(article_url + "\n\n\n")
                                break
                            break

    def tag_visible(self, element):
        if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
            return False
        if isinstance(element, Comment):
            return False
        return True

