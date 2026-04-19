from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


def fetch_url(url, timeout=5):
    req = Request(
        url,
        headers={"User-Agent": "MultiAgentCrawler/1.0"}
    )

    try:
        with urlopen(req, timeout=timeout) as response:
            content_type = response.headers.get("Content-Type", "")
            status_code = getattr(response, "status", 200)

            if "text/html" not in content_type.lower():
                return {
                    "success": False,
                    "url": url,
                    "status_code": status_code,
                    "html": "",
                    "error": f"Unsupported content type: {content_type}",
                }

            charset = response.headers.get_content_charset() or "utf-8"
            html = response.read().decode(charset, errors="replace")

            return {
                "success": True,
                "url": url,
                "status_code": status_code,
                "html": html,
                "error": None,
            }

    except HTTPError as e:
        return {
            "success": False,
            "url": url,
            "status_code": e.code,
            "html": "",
            "error": f"HTTP error: {e.reason}",
        }

    except URLError as e:
        return {
            "success": False,
            "url": url,
            "status_code": None,
            "html": "",
            "error": f"URL error: {e.reason}",
        }

    except Exception as e:
        return {
            "success": False,
            "url": url,
            "status_code": None,
            "html": "",
            "error": str(e),
        }