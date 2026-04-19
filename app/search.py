from app.utils import tokenize


class SearchEngine:
    def __init__(self, storage):
        self.storage = storage

    def search(self, query):
        terms = tokenize(query)
        rows = self.storage.search(terms)

        results = []
        for row in rows:
            results.append(
                (
                    row["page_url"],
                    row["origin_url"],
                    row["depth"],
                )
            )

        return results