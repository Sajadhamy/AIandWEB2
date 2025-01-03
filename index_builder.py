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


