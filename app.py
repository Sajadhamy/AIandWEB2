from flask import Flask, request, render_template_string
from index_builder_whoosh import initialize_index, search_index, add_to_index

app = Flask(__name__)

index_dir = "index"     #initialize the woosh indx dir
initialize_index(index_dir)

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

@app.route("/index", methods=["POST"])
def index():
    url = request.form.get("url")
    html = request.form.get("html")

    if not url or not html:
        return "URL and HTML content are required.", 400

    add_to_index(index_dir, url=url, html=html)
    return f"Indexed: {url}", 200


# Search route
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()   # request.args.get("q"): Extracts the q parameter from the URL.
                                                #strip(): Removes leading or trailing spaces from the query.
    if not query:       #handle empty query
        return "<h1>No search query provided!</h1>", 400

    results = search_index(query, index_dir)
    if results:
        result_items = [        #collect all the results into a list list
            f"""
            <li>
                <h3>{res['title']}</h3>
                <p>{res['teaser']}</p>
                <a href="{res['url']}" target="_blank">{res['url']}</a>
            </li>
            """
            for res in results
        ]
                    #<h3>{res['title']}</h3> displaying the title in bold
                    #<p>{res['teaser']}</p> display a short snippet of the content
                    #<a href="{res['url']}" target="_blank">{res['url']}</a> creating a clickable link for the url. target="_blank" opens the link in a new tab
        result_items_html = "".join(result_items) #join the list into a single string

        #return complete html
        return f"""
        <h1>Search Results for '{query}'</h1>
        <ul>
            {result_items_html}
        </ul>
        """
                    #<h1>: the query as a heading on the page
                    #<ul>: wraps the list of results in an unordered list
                    #{result_items}: inserts the formatted search results (<li> elements) inside the list.
    else:
        return f"<h1>No results found for '{query}'</h1>"
    
if __name__ == "__main__":
    app.run(debug=True)