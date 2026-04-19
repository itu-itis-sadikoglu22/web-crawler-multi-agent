from html.parser import HTMLParser
from app.utils import normalize_url


class SimpleHTMLParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self.text_parts = []
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    url = normalize_url(self.base_url, value)
                    if url:
                        self.links.append(url)

        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data.strip()

        text = data.strip()
        if text:
            self.text_parts.append(text)


def parse_html(base_url, html):
    parser = SimpleHTMLParser(base_url)
    parser.feed(html)


    return {
        "title": parser.title,
        "body": " ".join(parser.text_parts),
        "links": parser.links,
    }