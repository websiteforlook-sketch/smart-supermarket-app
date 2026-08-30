"""
product_images.py — Best-effort automatic product photo matching.

When products are imported in bulk (CSV/Excel) and a row has no image_url
(or the cell is blank), this module guesses a relevant stock photo from the
product name — "Basmati Rice" gets a rice photo, "Bath Soap" gets a soap
photo, "Pen" gets a pen photo, etc. If nothing in the name matches, it falls
back to the product's category, then to a generic grocery-product photo, so
imported rows never fall back to the plain placeholder box.

No API key required — uses Unsplash's public keyword-image endpoint
(source.unsplash.com). Each match is *resolved* once at import time (the
redirect is followed to a fixed images.unsplash.com URL) and that fixed URL
is what gets stored in the database — so the photo shown for a product
stays the same every time the page reloads, instead of changing randomly.
"""

import re
from functools import lru_cache

try:
    import requests
except ImportError:  # pragma: no cover - defensive, requests should be installed
    requests = None

# Ordered from most specific to least specific. The first keyword that
# appears as a whole word in the product name wins. Keep keywords lowercase.
# Feel free to add more rows here as you add new kinds of products.
_KEYWORD_QUERIES = [
    # Staples / grains
    ("basmati", "basmati rice"),
    ("rice", "rice bag"),
    ("atta", "wheat flour"),
    ("wheat", "wheat flour"),
    ("flour", "flour"),
    ("sugar", "sugar"),
    ("salt", "salt"),
    ("dal", "lentils dal"),
    ("pulses", "lentils"),
    ("besan", "gram flour"),
    ("poha", "flattened rice"),
    ("suji", "semolina"),
    ("rava", "semolina"),

    # Oils / dairy
    ("ghee", "ghee jar"),
    ("oil", "cooking oil bottle"),
    ("milk", "milk carton"),
    ("curd", "yogurt bowl"),
    ("yogurt", "yogurt bowl"),
    ("paneer", "paneer cheese"),
    ("butter", "butter block"),
    ("cheese", "cheese block"),

    # Beverages
    ("green tea", "green tea box"),
    ("tea", "tea leaves box"),
    ("coffee", "coffee jar"),
    ("juice", "fruit juice bottle"),
    ("cold drink", "soda bottle"),
    ("soda", "soda bottle"),
    ("water bottle", "water bottle"),
    ("water", "water bottle"),

    # Snacks
    ("biscuit", "biscuit packet"),
    ("cookie", "cookies"),
    ("chips", "potato chips packet"),
    ("namkeen", "indian namkeen snack"),
    ("chocolate", "chocolate bar"),
    ("candy", "candy"),
    ("ice cream", "ice cream tub"),
    ("noodles", "instant noodles packet"),
    ("maggi", "instant noodles packet"),

    # Bakery
    ("bread", "bread loaf"),
    ("bun", "bread buns"),
    ("egg", "eggs carton"),

    # Produce
    ("onion", "onions"),
    ("potato", "potatoes"),
    ("tomato", "tomatoes"),
    ("apple", "apples"),
    ("banana", "bananas"),
    ("vegetable", "fresh vegetables"),
    ("fruit", "fresh fruit"),

    # Spices
    ("masala", "indian spices"),
    ("spice", "indian spices"),
    ("turmeric", "turmeric powder"),
    ("chilli", "red chilli powder"),
    ("chili", "red chilli powder"),

    # Personal care
    ("soap", "bath soap bar"),
    ("shampoo", "shampoo bottle"),
    ("toothpaste", "toothpaste tube"),
    ("toothbrush", "toothbrush"),
    ("hand wash", "hand wash bottle"),
    ("sanitizer", "hand sanitizer bottle"),
    ("lotion", "body lotion bottle"),
    ("razor", "razor blade"),
    ("perfume", "perfume bottle"),
    ("deodorant", "deodorant spray"),
    ("tissue", "tissue box"),
    ("napkin", "paper napkins"),
    ("diaper", "baby diapers"),

    # Household
    ("detergent", "detergent powder"),
    ("washing powder", "detergent powder"),
    ("dishwash", "dish soap bottle"),
    ("phenyl", "floor cleaner bottle"),
    ("cleaner", "cleaning spray bottle"),
    ("mop", "cleaning mop"),
    ("broom", "broom"),
    ("matchbox", "matchbox"),
    ("candle", "candle"),
    ("agarbatti", "incense sticks"),
    ("incense", "incense sticks"),
    ("bulb", "light bulb"),
    ("battery", "batteries"),
    ("plastic bag", "plastic bags"),

    # Stationery
    ("pen", "ballpoint pen"),
    ("pencil", "pencil"),
    ("notebook", "notebook"),
    ("eraser", "eraser"),
    ("marker", "marker pen"),
    ("stapler", "stapler"),
    ("envelope", "envelope"),
    ("paper", "paper stack"),

    # Health
    ("mask", "face mask"),
    ("bandage", "bandage"),
    ("medicine", "medicine tablets"),
    ("syrup", "medicine syrup bottle"),
]

# Category-level fallback when nothing in the product name matched above.
_CATEGORY_QUERIES = {
    "grocery": "grocery items",
    "personal care": "personal care products",
    "snacks": "snacks packet",
    "beverages": "beverage bottles",
    "dairy": "dairy products",
    "bakery": "bakery bread",
    "produce": "fresh vegetables",
    "stationery": "stationery items",
    "household": "household cleaning supplies",
    "health": "pharmacy medicine",
}

_GENERIC_QUERY = "grocery store product"
_UNSPLASH_BASE = "https://source.unsplash.com/400x400/?"


def _match_query(name: str, category: str) -> str:
    """Pick the best search term for this product: name keyword > category > generic."""
    n = (name or "").strip().lower()
    if n:
        for keyword, query in _KEYWORD_QUERIES:
            if re.search(r"\b" + re.escape(keyword) + r"\b", n):
                return query

    c = (category or "").strip().lower()
    if c in _CATEGORY_QUERIES:
        return _CATEGORY_QUERIES[c]
    for cat_key, query in _CATEGORY_QUERIES.items():
        if cat_key in c:
            return query

    return _GENERIC_QUERY


@lru_cache(maxsize=256)
def _resolve(query: str) -> str:
    """
    Turn a search term into a fixed image URL.

    source.unsplash.com/...?query redirects to a *random* matching photo on
    every request, which would make a product's picture change each time the
    page reloads. So we follow that redirect once here and cache + return
    the final images.unsplash.com URL, which is stable. If the request
    fails for any reason (no internet at import time, Unsplash down, etc.)
    we fall back to the redirecting URL itself — it still renders a photo,
    it just isn't guaranteed to be the exact same photo on every reload.
    """
    source_url = _UNSPLASH_BASE + query.replace(" ", "%20")
    if requests is None:
        return source_url
    try:
        resp = requests.get(source_url, allow_redirects=True, timeout=5)
        if resp.url and resp.url.startswith("http"):
            return resp.url
    except requests.RequestException:
        pass
    return source_url


def guess_image_url(name: str, category: str = "") -> str:
    """
    Best-effort product photo based on name, falling back to category, then
    a generic grocery photo. Always returns a usable URL.

    Only call this when the import sheet didn't already supply its own
    image_url — this is a guess, not an authoritative photo, and a
    shopkeeper can always override it later from the Edit panel.
    """
    query = _match_query(name, category)
    return _resolve(query)
