"""
Live news feed — Alpha Vantage NEWS_SENTIMENT API.
Pulls recent financial/geopolitical news for manual selection into the
intelligence pipeline. Free tier: 25 requests/day — cache aggressively.
"""

from __future__ import annotations

import os
import requests

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

# Topics relevant to geopolitical/commodity risk — see Alpha Vantage docs
# for the full topic list. These three cover macro shocks, energy/supply
# chain disruption, and general financial market impact.
DEFAULT_TOPICS = "economy_macro,energy_transportation,finance"


def fetch_live_headlines(max_results: int = 10, topics: str = DEFAULT_TOPICS) -> list[dict]:
    """
    Fetch recent financial/geopolitical news from Alpha Vantage.

    Returns a list of dicts: {title, url, source, time_published, sentiment}.
    Raises RuntimeError on network/API/quota failure — caller should catch
    and show a clean message rather than crash the UI.
    """
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ALPHA_VANTAGE_API_KEY not set — add it to your .env file. "
            "Get a free key at https://www.alphavantage.co/support/#api-key"
        )

    params = {
        "function": "NEWS_SENTIMENT",
        "topics": topics,
        "sort": "LATEST",
        "limit": max_results,
        "apikey": api_key,
    }

    try:
        resp = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=25)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not reach Alpha Vantage news feed: {e}") from e
    except ValueError as e:
        raise RuntimeError(f"Alpha Vantage returned an unreadable response: {e}") from e

    # Alpha Vantage signals rate-limit / quota issues via a "Note" or
    # "Information" field in the JSON body, not an HTTP error code.
    if "Note" in data or "Information" in data:
        msg = data.get("Note") or data.get("Information")
        raise RuntimeError(f"Alpha Vantage API limit reached: {msg}")

    feed = data.get("feed", [])
    if not feed:
        return []

    results = []
    for item in feed[:max_results]:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        results.append(
            {
                "title": title,
                "url": item.get("url", ""),
                "source": item.get("source", ""),
                "time_published": item.get("time_published", ""),
                "sentiment": item.get("overall_sentiment_label", ""),
            }
        )
    return results









# """
# Live news feed — GDELT DOC 2.0 API (free, no API key required).
# Pulls recent geopolitical/commodity-relevant headlines for manual selection
# into the intelligence pipeline.
# """

# from __future__ import annotations

# import requests

# GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

# # Keyword filter — tuned toward the kind of events this system is built to analyze
# DEFAULT_QUERY = (
#     '(sanctions OR "trade war" OR tariff OR "export control" OR "supply chain" '
#     'OR strait OR pipeline OR OPEC OR "rare earth" OR blockade OR conflict '
#     'OR "shipping lane" OR embargo) sourcelang:english'
# )


# def fetch_live_headlines(max_results: int = 10, query: str = DEFAULT_QUERY) -> list[dict]:
#     """
#     Fetch recent geopolitical/commodity-relevant headlines from GDELT.

#     Returns a list of dicts: {title, url, seendate, domain}.
#     Raises RuntimeError on network/API failure — caller should catch and
#     show a clean message rather than crash the UI.
#     """
#     params = {
#         "query": query,
#         "mode": "artlist",
#         "maxrecords": max_results,
#         "format": "json",
#         "sort": "datedesc",
#     }

#     try:
#         resp = requests.get(GDELT_DOC_API, params=params, timeout=25)
#         resp.raise_for_status()
#         data = resp.json()
#     except requests.exceptions.RequestException as e:
#         raise RuntimeError(f"Could not reach GDELT news feed: {e}") from e
#     except ValueError as e:
#         raise RuntimeError(f"GDELT returned an unreadable response: {e}") from e

#     articles = data.get("articles", [])
#     if not articles:
#         return []

#     seen_titles = set()
#     results = []
#     for a in articles:
#         title = a.get("title", "").strip()
#         if not title or title in seen_titles:
#             continue
#         seen_titles.add(title)
#         results.append(
#             {
#                 "title": title,
#                 "url": a.get("url", ""),
#                 "seendate": a.get("seendate", ""),
#                 "domain": a.get("domain", ""),
#             }
#         )
#     return results