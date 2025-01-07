from flask import Flask, request, render_template_string
from index_builder_whoosh import initialize_index, search_index

app = Flask(__name__)

INDEX_DIR = "index"     #initialize the woosh ndx dir
initialize_index(INDEX_DIR)

#home route:
@app.route("/")
def home():             #return a simple html page with a search form
    return render_template_string("""
    <h1>Search Engine</h1>
    <form action="/search" method="get">
        <input type="text" name="q" placeholder="Enter your search query" required>
        <button type="submit">Search</button>
    </form>
    """)

                        #<form> sends a GET request to /search when submitted.
                        #<input> is a text box where the user enters their query.
                        #<button> is a submit button.


# Search route
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()   # request.args.get("q"): Extracts the q parameter from the URL.
                                                #strip(): Removes leading or trailing spaces from the query.
    if not query:       #handle empty query
        return "<h1>No search query provided!</h1>", 400

    results = search_index(INDEX_DIR, query)
    if results:
        links = "".join([f'<li><a href="{url}">{url}</a></li>' for url in results])     #for each URL in the results, create an HTML <li> with a link (<a>).
        return f"<h1>Search Results for '{query}'</h1><ul>{links}</ul>"
    else:
        return f"<h1>No results found for '{query}'</h1>"
    
if __name__ == "__main__":
    app.run(debug=True)