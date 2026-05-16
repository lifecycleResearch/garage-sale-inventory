"""Price comparison engine using DuckDuckGo and web search."""
import json
import re
import urllib.request
from typing import Dict, List


def search_comps(query: str, max_results: int = 5) -> List[Dict]:
    """Search DuckDuckGo for price comps on an item.

    Returns list of {title, url, snippet, extracted_price} dicts.
    """
    # DuckDuckGo HTML search (no API key required)
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query + ' price sold')}"  # noqa: E501
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }

    req = urllib.request.Request(search_url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8")
    except Exception as exc:
        return [{"title": "Search error", "url": "", "snippet": str(exc), "extracted_price": None}]

    results = []
    # Simple regex parsing of DDG HTML results
    result_blocks = re.findall(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?(?=<a[^>]+class="result__a"|$)',
        html,
        re.DOTALL | re.IGNORECASE,
    )

    for url, title_html in result_blocks[:max_results]:
        title = re.sub(r'<[^>]+>', '', title_html).strip()
        # Extract price patterns like $123, $1,234.56, £50, €30
        price_match = re.search(r'[$€£]([\d,]+\.?\d*)', title)
        price = None
        if price_match:
            try:
                price = float(price_match.group(1).replace(',', ''))
            except ValueError:
                price = None

        results.append({
            "title": title,
            "url": url,
            "snippet": title,  # Simplified
            "extracted_price": price,
        })

    return results


def suggest_price(results: List[Dict]) -> Dict:
    """Suggest a price based on comp search results."""
    prices = [r["extracted_price"] for r in results if r.get("extracted_price")]
    if not prices:
        return {"suggested_price": None, "range_low": None, "range_high": None, "confidence": "low"}

    prices.sort()
    median = prices[len(prices) // 2]
    low = prices[0] if len(prices) >= 2 else median * 0.7
    high = prices[-1] if len(prices) >= 2 else median * 1.3

    # For garage sales, suggest below median
    suggested = round(median * 0.75, 2)

    return {
        "suggested_price": suggested,
        "range_low": round(low, 2),
        "range_high": round(high, 2),
        "median": round(median, 2),
        "confidence": "medium" if len(prices) >= 3 else "low",
        "source_count": len(prices),
    }


def find_comps(item_name: str, brand: str = "", category: str = "") -> Dict:
    """Full comp search pipeline for an item."""
    query = f"{brand} {item_name} {category}".strip()
    results = search_comps(query)
    suggestion = suggest_price(results)
    return {"query": query, "results": results, "suggestion": suggestion}
