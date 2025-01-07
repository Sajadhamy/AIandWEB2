import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
from whoosh.qparser import QueryParser
from bs4 import BeautifulSoup

schema = Schema(
    url = ID(stored=True, unique=True),     #unique identifier for the page
    title = TEXT(stored=True),               #title of the page
    teaser = TEXT(stored=True),              #teaser\snippet of the page
    content = TEXT(stored= True))           #text content of the page


def initialize_index(index_dir="index"):
    """
    Initialize the Whoosh index in the specified directory or creat the dir.
    """
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    return create_in(index_dir, schema)

# Add documents to the index
def add_to_index(index_dir="index", url=None, html=None):
    """
    Add a document to the index.
    index_dir: Directory where the index is stored.
    url: The URL of the page.
    html: The html content of the page.
    """
    ix = open_dir(index_dir)
    writer = AsyncWriter(ix)
    soup = BeautifulSoup(html, "html.parser")
    if soup.title:
        title = soup.title.string.strip()
    else:
        "No Title"
    
    # extract a teaser/snippet (use meta description or first 200 characters of text)
    teaser = ""
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc and meta_desc.get("content"):
        teaser = meta_desc["content"].strip()
    else:       # get first 200 characters of visible text
        visible_text = ' '.join(soup.stripped_strings)
        teaser = visible_text[:200] + "..." if len(visible_text) > 200 else visible_text

    content = ' '.join(soup.stripped_strings)       #extract the full content

    writer.add_document(url=url, title=title, teaser=teaser, content=content)      #add the doc to the indx
    writer.commit()


# Search the index
def search_index(query, index_dir="index"):
    """
    Search the index for a specific query.
    query: The query string to search for.
    index_dir: Directory where the index is stored.
    Returns a list of URLs matching the query.
    """
    ix = open_dir(index_dir)
    with ix.searcher() as searcher:
        parser = QueryParser("content", ix.schema)
        parsed_query = parser.parse(query)
        results = searcher.search(parsed_query)
        for result in results:
            return [
                {"url": result["url"], "title": result["title"], "teaser": result["teaser"]}
            ]

