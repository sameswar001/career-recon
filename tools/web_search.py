"""Web search tool for the researcher node, backed by Tavily.

Wrapping Tavily behind this function (rather than calling the client
directly inside the node) keeps the researcher node testable — tests
monkeypatch search_company and never need a real TAVILY_API_KEY.
"""

import os

from tavily import TavilyClient

DEFAULT_MAX_RESULTS = 5


def search_company(company: str, max_results: int = DEFAULT_MAX_RESULTS) -> list[dict]:
    """Returns a list of {content, source_url} dicts for the given company."""
    client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    response = client.search(
        query=f"{company} recent news, funding, product direction",
        max_results=max_results,
    )
    return [
        {"content": r["content"], "source_url": r["url"]}
        for r in response.get("results", [])
    ]
