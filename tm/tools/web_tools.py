"""
TM Web & Research Tools (DuckDuckGo Live Search & Scraper)
"""

import re
import urllib.request
from typing import Dict, Any, List
from tm.tools.base import tool

try:
    # pyrefly: ignore[missing-import]
    from ddgs import DDGS
except ImportError:
    import importlib
    try:
        _ddg_mod = importlib.import_module("duckduckgo_search")
        DDGS = getattr(_ddg_mod, "DDGS", None)
    except ImportError:
        DDGS = None


@tool(
    name="search_web_duckduckgo",
    description="Performs an online web search using DuckDuckGo (100% free, real-time results).",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query terms or topic to look up.",
            },
            "max_results": {
                "type": "integer",
                "description": "Max number of search results to return (default: 5).",
                "default": 5,
            },
        },
        "required": ["query"],
    },
    tier=1,
)
def search_web_duckduckgo(query: str, max_results: int = 5) -> Dict[str, Any]:
    if DDGS is not None:
        try:
            ddgs = DDGS()
            results = list(ddgs.text(query, max_results=max_results))
            formatted = []
            for r in results:
                formatted.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "snippet": r.get("body"),
                })
            return {"status": "success", "query": query, "results": formatted}
        except Exception as e:
            pass

    # HTML API fallback
    try:
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Basic regex scrape of title and snippet
        matches = re.findall(r'<a class="result__url" href="([^"]+)".*?<a class="result__snippet[^>]*>(.*?)</a>', html, re.DOTALL)
        results = []
        for href, snip in matches[:max_results]:
            clean_snip = re.sub(r"<[^>]+>", "", snip).strip()
            results.append({"url": href.strip(), "snippet": clean_snip})
        return {"status": "success", "query": query, "results": results}
    except Exception as e:
        return {"status": "error", "message": f"Web search failed: {e}"}


@tool(
    name="fetch_webpage_markdown",
    description="Fetches a public web page and extracts its readable text content.",
    parameters={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "The full HTTP/HTTPS URL to fetch.",
            }
        },
        "required": ["url"],
    },
    tier=1,
)
def fetch_webpage_markdown(url: str) -> Dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Strip scripts, styles, and tags
        text = re.sub(r"<(script|style).*?</\1>", "", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines[:300])  # Cap at 300 lines

        return {
            "status": "success",
            "url": url,
            "content": clean_text[:4000],  # Return up to 4000 chars
        }
    except Exception as e:
        return {"status": "error", "message": f"Failed to fetch webpage: {e}"}
