from collections import defaultdict
from index_builder import build_index, search

index = defaultdict(list)
build_index("<html><body>Python Crawler</body></html>", "http://example.com/page1", index)
build_index("<html><body>Python Web</body></html>", "http://example.com/page2", index)

result = search(["python", "crawler"], index)
print("search result:", result)