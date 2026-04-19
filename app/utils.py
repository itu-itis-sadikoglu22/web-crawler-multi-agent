import re
from urllib.parse import urljoin, urlparse


def normalize_url(base_url, link):
    if not link:
        return None

    url = urljoin(base_url, link)
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return None

    normalized = parsed._replace(fragment="").geturl()
    return normalized


def tokenize(text):
    text = text.lower()
    words = re.findall(r"[a-z0-9]+", text)
    return words


def term_frequencies(text):
    tokens = tokenize(text)
    freq = {}

    for t in tokens:
        freq[t] = freq.get(t, 0) + 1

    return list(freq.items())