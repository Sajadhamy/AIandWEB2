from flask import Flask, request, render_template, url_for
from markupsafe import Markup
from AIandWEB2.index_builder_whoosh import initialize_index, search_index, add_to_index

app = Flask(__name__)

index_dir = "index"     #initialize the woosh indx dir
initialize_index(index_dir)


@app.route("/")
def home():             #Render a search form.
    return render_template("home.html")


@app.route("/index", methods=["POST"])
def index():
    url = request.form.get("url")
    html = request.form.get("html")

    if not url or not html:
        return "URL and HTML content are required.", 400
    try:
        add_to_index(index_dir, url=url, html=html)
        return f"Indexed: {url}", 200
    except Exception as e:
        return f"Error indexing URL {url}: {e}", 500


@app.route("/search", methods =["GET"])
def search():
    query = request.args.get("q", "").strip()   # request.args.get("q"): Extracts the q parameter from the URL.
                                                #strip(): Removes leading or trailing spaces from the query.
    if not query:       #handle empty query
        return render_template("error.html", message="No search query provided!"), 400

    results = search_index(query, index_dir)
    if results:
        return render_template("results.html", query=query, results=results, Markup=Markup)
    else:
        return render_template("no_results.html", query=query)

    
if __name__ == "__main__":
    app.run(debug=True)