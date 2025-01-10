import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.index import create_in, open_dir
from whoosh.writing import AsyncWriter
from whoosh.qparser import QueryParser, MultifieldParser
from bs4 import BeautifulSoup

schema = Schema(
    url = ID(stored=True, unique=True),      #unique identifier for the page
    title = TEXT(stored=True),               #title of the page
    teaser = TEXT(stored=True),              #teaser\snippet of the page
    content = TEXT(stored= True)             #text content of the page

)          

def initialize_index(index_dir="index"):
    """
    initialize the Whoosh index in the specified directory or creat the dir.
    """
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
        print(f"Initializing new index at {index_dir}...")   
        return create_in(index_dir, schema)
    else:
        print(f"opening existing index at {index_dir}...")
        return open_dir(index_dir)
   
def add_to_index(index_dir="index", url=None, html=None):
    """
    Add a document to the index.
    index_dir: Directory where the index is stored.
    url: The URL of the page.
    html: The html content of the page.
    """
    try:
        ix = open_dir(index_dir)
        writer = AsyncWriter(ix)    #create an asynchronous writer to add or modify documents in the indx
        writer.delete_by_term("url", url)   #delete already existing dosc to avoide duplicates
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string.strip() if soup.title else "No Title"
    
        
        meta_desc = soup.find("meta", {"name": "description"})      # extract a teaser/snippet use meta description or first 200 characters of text
        teaser = (
            meta_desc["content"].strip()
            if meta_desc and meta_desc.get("content")
            else ' '.join(soup.stripped_strings)[:200] + "..."
        )
        content = ' '.join([tag.get_text() for tag in soup.find_all(['p', 'div'])if tag.get_text()])       #extract the full content

        writer.add_document(url=url, title=title, teaser=teaser, content=content)      #add the doc to the indx
        writer.commit()
        print(f"indexed {url}. Index now contains {ix.doc_count()} documents.")
    except Exception as e:
        print(f"Error indexing URL {url}: {e}")


def search_index(query, index_dir="index"):
    """
    Search the index for a specific query.
    query: The query string to search for.
    index_dir: Directory where the index is stored.
    Returns a list of URLs matching the query.
    """
    try:
        ix = open_dir(index_dir)
        with ix.searcher() as searcher:
            parser = MultifieldParser(["title", "teaser", "content"], schema=ix.schema)
            parsed_query = parser.parse(query)
            results = searcher.search(parsed_query)
            return [
                {
                    "url": result["url"],
                    "title": result["title"],
                    "teaser": result.highlights("content") or result["teaser"]
                }
                for result in results
            ]
    except Exception as e:
        print(f"Error searching index {e}")
        return []
    
#just for testing
if __name__ == "__main__":
    index_dir = "index"
    initialize_index(index_dir)

    sample_html = """
    <html>
        <head><title>Sample Page</title><meta name="description" content="This is a sample meta description."></head>
        <body>
            <p>This is some sample content for the test page. It contains useful information about the topic.</p>
            <p>More details are provided in this paragraph.</p>
        </body>
    </html>
    """
    add_to_index(index_dir, url="http://example.com", html=sample_html)

    results = search_index("sample", index_dir)
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Title: {result['title']}")
        print(f"Teaser: {result['teaser']}")
        print()