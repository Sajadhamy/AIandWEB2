from collections import defaultdict
from index_builder import build_index

html_content = """
<html>
<head><title>Test Page</title></head>
<body>
    <h1>Welcome to the Test Page</h1>
    <p>This is a simple HTML page for testing the index builder.</p>
</body>
</html>
"""
url = "http://example.com/test"

index = defaultdict(list)
build_index(html_content, url, index)


for word, urls in index.items():
    print(f"{word}: {urls}")
    