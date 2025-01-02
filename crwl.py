import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin #to join the base url with the relative url

class WebCrawler:
    def __init__(self, baseURL, max_depth = 2):
        """
        initializing the crawler
        baseURL: starting URL
        max_depth: depths of the links to follow
        """
        self.baseURL = baseURL
        self.max_depth = max_depth
        self.visitedURLs = set() #initialize an empty set as a it remember the URLs that already visited

    def fetch_page(self, url):
        """
        to fetch the HTML content of the URL.
        url: the URL to fetch
        returns the content as a string or None if it fails.
        """
        try: 
            response = requests.get(url)    #retrieve the url in 5 sec
            if response.status_code == 200: #checking the request status is successful
                return response.text        #returning the content as s string
            else:                           #if the request is not successful return nothing
                print(f"Fail to fetch{url}. Status code: P{response.status_code}")
                return None
        except requests.RequestException as e: 
                                            #all other possible errors return nothing 
            print(f"Error fetching {url}: {e}")
            return None
        
    def parse_links(self, html, baseURL):
        """
        extracting hyperlinks from the html content
        html: the html content of the page
        return a list of absolute urls
        """
        soup = BeautifulSoup(html,"html parser")
        links = []                                      #initializing the list of URLs

        for tag in soup.find_all("a", href = True):     #finding all the hyperlinks
            relativeURL = tag['href']
            absoluteURL = urljoin(baseURL, relativeURL) #resolve the urls to an absolute format
            if absoluteURL.startswith("http"):          #filtering only http links
                links.append(absoluteURL)

        return links


    def crawl(self, URL, depth = 0):
        """
        exploring links and exteacting contents
        url: the strarting url
        depth: how deep the crawler is
        """
        if depth > self.max_depth:                  #checking the depth so it doesn't crawl more than neccesary
            return
        if URL in self.visitedURLs:                 #recently visited pages doesn't need to be crawled again and preventing infinite loops
            return
        print(f"crawling {URL} in depth {depth}")   #just to see what going on

        html = self.fetch_page(URL)                 #downloading the current url's page
        if not html:
            return
        
        self.visitedURLs.add(URL)                   #adding the currnt url to visited ones

        links = self.parse_links(URL)               #extracting all the valid links 

        for link in links:                          #crawling the links
            self.crawl(link, depth + 1)

