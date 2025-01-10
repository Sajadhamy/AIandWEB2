import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse #to join the base url with the relative url and extract the domain of each link
from index_builder_whoosh import initialize_index, add_to_index
from urllib.robotparser import RobotFileParser
import os


class WebCrawler:
    def __init__(self, baseURL="https://vm009.rz.uos.de/crawl/index.html", max_depth = 5, index_dir="index", max_pages = 100):
        """
        initializing the crawler
        baseURL: starting URL
        max_depth: depths of the links to follow
        index_dir: dir for the whoosh indx
        max_pages: Maximum number of pages to crawl
        """
        self.baseURL = baseURL
        self.max_depth = max_depth
        self.index_dir = index_dir
        self.max_pages = max_pages
        self.visitedURLs = set() #initialize an empty set as a it remember the URLs that already visited
        self.page_count = 0
        self.base_domain = urlparse(baseURL).netloc #extract and store the domain of the base url
        
        

        if not os.path.exists(index_dir): #initialize whoosh indx
            os.mkdir(index_dir)
        initialize_index(index_dir)

        #setup robots.txt parser
        self.robot_parser = RobotFileParser()   #handle th rules defined in robots.txt file of the website being crawled to tell crawlers which parts of the site are allowed or disallowed for crawling
        self.robot_parser.set_url(urljoin(baseURL, "/robots.txt"))
        self.robot_parser.read()
    
    def is_allowed(self, url):
        """
        Check if a URL is allowed to be crawled based on robots.txt rules.
        """
        return self.robot_parser.can_fetch("*", url)
    
    def fetch_page(self, url):
        """
        to fetch the HTML content of the URL.
        url: the URL to fetch
        returns the content as a string or None if it fails.
        """
        try: 
            response = requests.get(url, timeout=5)    #retrieve the url in 5 sec
            if response.status_code == 200 and "text/html" in response.headers.get("Content-type", ""):            #checking the request status is successful and is an HTML
                response.encoding = response.apparent_encoding
                return response.text                   #returning the content as s string
            else:                                      #if the request is not successful return nothing
                print(f"Skipped non-HTML or unsuccessful response: {url} (Statues: {response.status_code})")
                return None
        except requests.RequestException as e: 
                                            #all other possible errors return nothing 
            print(f"Error fetching {url}: {e}")
            return None
        
    def parse_links(self, html, currentURL):
        """
        extracting hyperlinks from the html content
        html: the html content of the page
        return a list of absolute urls
        """
        soup = BeautifulSoup(html,"html.parser")
        links = []                                      #initializing the list of URLs

        for tag in soup.find_all("a", href = True):     #finding all the hyperlinks
            relativeURL = tag['href']
            absoluteURL = urljoin(currentURL, relativeURL) #resolve the urls to an absolute format
            parsedURL = urlparse(absoluteURL)
            if parsedURL.netloc == self.base_domain:          #filtering only the links within the same domain
                normalized_url = self.normalize_url(absoluteURL)
                links.append(normalized_url)

        return links
    
    @staticmethod
    def normalize_url(url):
        """
        Normalize a URL to ensures that URLs are stored
        in a consistent format by removing fragments and query strings.
        """
        parsed = urlparse(url)
        return parsed.scheme + "://" + parsed.netloc + parsed.path


    def crawl(self, URL, depth = 0):
        """
        exploring links and exteacting contents
        url: the strarting url
        depth: how deep the crawler is
        """
        if depth > self.max_depth or self.page_count >= self.max_pages:  #checking the depth and page count so it doesn't crawl more than neccesary
            return
        
        normalized_url = self.normalize_url(URL)
        if normalized_url in self.visitedURLs:        #recently visited pages doesn't need to be crawled again and preventing infinite loops
            return
        if not self.is_allowed(URL):       
            print(f"skipping disallowed url: {URL}")
            return
        
        print(f"crawling {URL} in depth {depth}")   #just to see what going on

        html = self.fetch_page(URL)                 #downloading the current url's page

        if html:                                    #add the contnt to the woosh indx
            add_to_index(self.index_dir, URL, html)

            self.visitedURLs.add(normalized_url)                   #adding the currnt url to visited ones
            self.page_count += 1
            links = self.parse_links(html, URL)               #extracting all the valid links 

            for link in links:                          #crawling the links
                self.crawl(link, depth + 1)


if __name__ == "__main__":          #instantiate the WebCrawler with the base URL.
    crawler = WebCrawler()
    crawler.crawl(crawler.baseURL)