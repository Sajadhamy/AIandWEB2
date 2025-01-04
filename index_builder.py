from collections import defaultdict     #to handle dictionaries easier
import re   #for text processing
from bs4 import BeautifulSoup

def build_index(html, url, index):
    """
    an in-memory index from the html content

    html (str): The HTML content of the page.
    url (str): The URL of the page.
    index (defaultdict): The dictionary where the index is stored.
    """

    soup = BeautifulSoup(html, "html.parser")       #parse the html
    text = soup.get_text(separator=" ")             #extract the visible text
    words = re.findall(r'\b\w+\b', text.lower())    #regular expressions to tokenize the text

    for word in words:
        if url not in index[word]:
            index[word].append(url)

def search(words, index):
    """
    a function that iterate through an index to find URLs on a list of words
    word: a list of words to search for
    index: the in-memory index dictionary
    returns a list of URLs containing all the words
    """
    list_of_URLs= []
    
    for word in words:                              #check if the word is in the index and add the url as a set to the list 
        if word in index:
            list_of_URLs.append(set(index[word]))
        else:       #if not in the index then no url should be added
            return []
    
    if list_of_URLs:        # Find the intersection of all URL sets
        common_URLs = set.intersection(*list_of_URLs)
    else:
        set()
        
    return list(common_URLs)