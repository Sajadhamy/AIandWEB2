import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
from whoosh.qparser import QueryParser

schema = Schema(
    url = ID(stored=True, unique=True),     #unique identifier for the page
    content = TEXT(stored= True))           #text content of the page


def initialize_index(index_dir="index"):
    """
    Initialize the Whoosh index in the specified directory or creat the dir.
    """
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    return create_in(index_dir, schema)

# Add documents to the index
def add_to_index(index_dir="index", url=None, content=None):
    """
    Add a document to the index.
    index_dir: Directory where the index is stored.
    url: The URL of the page.
    content: The text content of the page.
    """
    ix = open_dir(index_dir)
    writer = AsyncWriter(ix)
    writer.add_document(url=url, content=content)
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
        return [result['url'] for result in results]
