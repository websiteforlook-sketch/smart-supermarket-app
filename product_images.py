"""
product_images.py — Automatic product image matching.

Two image sources are supported for a product:
  1. A bundled hand-drawn SVG icon, matched from the product name/category —
     100% offline, instant, and always relevant to the *category* of item
     even if not a literal photo of the exact product. This is the default
     for every new product.
  2. A real photo, found via Openverse's free, keyless, openly-licensed
     image-search API (https://api.openverse.org). This is opt-in only,
     through the "Review real photos" flow on the Products page — a human
     always looks at candidates and picks one before it's saved. Openverse
     indexes openly-licensed creative/historical photography (old adverts,
     museum scans, Flickr, etc.), NOT a curated product-photo catalog, so a
     keyword search can return something technically tagged with the right
     word but visually irrelevant (an antique soap advertisement for "bath
     soap", a landscape for "sunflower oil"). That's a structural limit of
     this free source, not something query-tuning fully solves — which is
     why results are never saved without a person choosing one.

Storage convention
-------------------
guess_image_tag() returns a short tag like "rice" or "personal_care".
Callers (db.py) store this in the products.image_url column as the string
"icon:<tag>" (e.g. "icon:rice") — NOT the SVG itself — so the column stays
tiny. At render time, get_icon_data_uri() turns "icon:<tag>" back into an
actual displayable image. Anything that isn't an "icon:" value (i.e. a real
http(s) URL, whether pasted in by a shopkeeper or approved through the photo
review flow) is passed through untouched — see is_live_photo() below.
"""

import base64
import re
from functools import lru_cache

try:
    import requests
except ImportError:  # pragma: no cover - requests should be in requirements.txt
    requests = None

# ---------------------------------------------------------------------------
# Real product photos (Openverse — free, keyless, openly-licensed image
# search: https://openverse.org / https://api.openverse.org).
#
# IMPORTANT: this is only ever called from the "Review real photos" flow in
# app.py, which shows a few candidates to the shopkeeper and requires them
# to tap "Use this photo" before anything is saved. Nothing here writes to
# the database directly or runs unattended.
# ---------------------------------------------------------------------------

_OPENVERSE_SEARCH_URL = "https://api.openverse.org/v1/images/"
_WEB_PHOTO_TIMEOUT_SECONDS = 4


def _build_search_query(name: str, category: str) -> str:
    """Turn a product name into a decent photo-search query, e.g.
    'Basmati Rice 5kg' -> 'basmati rice', 'Bath Soap' -> 'bath soap'."""
    n = re.sub(r"\b\d+\s?(kg|g|ml|l|pcs|pack|packs)\b", "", (name or "").lower())
    n = re.sub(r"[^a-z\s]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n or (category or "product").strip().lower()


@lru_cache(maxsize=256)
def fetch_web_photo_candidates(name: str, category: str = "", count: int = 3) -> tuple:
    """
    Search the open web (via Openverse's free, keyless image-search API)
    for real photos of this product and return up to `count` candidate
    https:// image URLs as a tuple, best match first. Returns an empty
    tuple if anything goes wrong (no internet, no results, timeout, etc.)
    — callers should fall back to an auto-picked icon in that case.

    IMPORTANT: automated keyword search can return a wrong or irrelevant
    photo (it has no real understanding of the product). Don't display a
    candidate to customers/on a live storefront without a human picking
    it first — see app.py's "Review real photos" flow, which is the only
    place this function is called from.
    """
    if requests is None:
        return ()
    query = _build_search_query(name, category)
    if not query:
        return ()
    try:
        resp = requests.get(
            _OPENVERSE_SEARCH_URL,
            params={
                "q": query,
                "page_size": max(count, 3),
                "mature": "false",
            },
            timeout=_WEB_PHOTO_TIMEOUT_SECONDS,
            headers={"User-Agent": "SmartMart-Inventory-App/1.0"},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        urls = []
        for item in results:
            url = item.get("url") or item.get("thumbnail")
            if url and url.startswith("http"):
                urls.append(url)
            if len(urls) >= count:
                break
        return tuple(urls)
    except Exception:
        return ()


def fetch_web_photo(name: str, category: str = "") -> str | None:
    """
    Best-guess single photo URL (first candidate), or None.

    NOT used anywhere in the unattended add/bulk-import path anymore — see
    the module note above about why an unreviewed pick from this source is
    risky. Kept only for callers that explicitly want a single best guess
    to show a human for approval.
    """
    candidates = fetch_web_photo_candidates(name, category, count=1)
    return candidates[0] if candidates else None

# ---------------------------------------------------------------------------
# Icon artwork.
#
# Two visual families live in here side by side:
#   - The original "flat design + long shadow" icons (100x100, rounded
#     colored background square, drop-shadow triangle) — most tags below.
#   - A newer "bold outline clip-art with a text label" style — currently
#     just milk / bread / chips / yogurt, added on request to match a set
#     of reference images. These have no background square (transparent),
#     a thick dark outline, flatter color fills, and the product name
#     baked in as bold text, the same way a shelf-label sticker would read.
#     Feel free to redraw any of the older tags in this same style later —
#     just replace the entry below and everything else (matching, storage,
#     rendering) keeps working unchanged.
# ---------------------------------------------------------------------------

ICON_SVGS = {
    "rice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#94A3AE"/>

<path d="M26,88 L74,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M30 40 Q26 64 34 84 Q37 90 50 90 Q63 90 66 84 Q74 64 70 40 Q50 48 30 40Z" fill="#E8C77E"/>
<path d="M50 48 Q60 46 70 40 Q50 30 30 40 Q40 46 50 48Z" fill="#C9A85C"/>
<path d="M42 40 Q42 30 50 26 Q58 30 58 40" fill="none" stroke="#C9A85C" stroke-width="5" stroke-linecap="round"/>
<ellipse cx="50" cy="26" rx="6" ry="4" fill="#C9A85C"/>
<circle cx="44" cy="60" r="2.4" fill="#FFFFFF"/>
<circle cx="56" cy="66" r="2.4" fill="#FFFFFF"/>
<circle cx="48" cy="74" r="2.4" fill="#FFFFFF"/>

</svg>
""",

    "grain": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#3EB4C4"/>

<path d="M28,88 L72,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M30 46 L70 46 L67 88 L33 88Z" fill="#D8A85C"/>
<path d="M30 46 L38 30 L62 30 L70 46Z" fill="#B98A3E"/>
<rect x="38" y="30" width="24" height="7" fill="#F3ECDD"/>
<line x1="38" y1="58" x2="62" y2="58" stroke="#B98A3E" stroke-width="2" opacity="0.6"/>
<line x1="38" y1="70" x2="60" y2="70" stroke="#B98A3E" stroke-width="2" opacity="0.6"/>

</svg>
""",

    "sugar": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8B84B"/>

<path d="M30,88 L70,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M36 40 Q30 60 34 84 Q35 90 46 90 L54 90 Q65 90 66 84 Q70 60 64 40 Q50 46 36 40Z" fill="#FFFFFF"/>
<path d="M44 40 Q46 30 50 22 Q54 30 56 40Z" fill="#E7E8F0"/>
<circle cx="43" cy="56" r="2.2" fill="#F472B6"/>
<circle cx="55" cy="62" r="2.2" fill="#818CF8"/>
<circle cx="47" cy="70" r="2.2" fill="#F472B6"/>
<circle cx="58" cy="52" r="2.2" fill="#818CF8"/>

</svg>
""",

    "salt": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8836E"/>

<path d="M32,88 L68,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="34" y="38" width="32" height="50" rx="6" fill="#FFFFFF"/>
<rect x="50" y="38" width="16" height="50" rx="6" fill="#DCEFF3"/>
<ellipse cx="50" cy="30" rx="17" ry="8" fill="#2A93B8"/>
<ellipse cx="50" cy="30" rx="17" ry="8" fill="none" stroke="#DCEFF3" stroke-width="1.5" opacity="0.4"/>
<circle cx="44" cy="29" r="1.4" fill="#DCEFF3"/>
<circle cx="50" cy="27" r="1.4" fill="#DCEFF3"/>
<circle cx="56" cy="29" r="1.4" fill="#DCEFF3"/>

</svg>
""",

    "bottle_oil": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#9FB768"/>

<path d="M32,88 L68,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="42" y="14" width="16" height="12" rx="2" fill="#C99A2B"/>
<path d="M38 26 L62 26 L68 42 L68 84 L32 84 L32 42Z" fill="#F4C15C"/>
<path d="M56 26 L62 26 L68 42 L68 84 L56 84Z" fill="#C99A2B"/>
<rect x="38" y="50" width="24" height="22" rx="2" fill="#FFF9EC"/>

</svg>
""",

    "dairy": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#C9BFAE"/>

<path d="M26,88 L74,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M32 46 L32 84 L68 84 L68 46 L50 24 Z" fill="#FFFFFF"/>
<path d="M50 24 L68 46 L68 84 L50 84Z" fill="#DCEBFB"/>
<path d="M40 34 L50 24 L60 34" fill="none" stroke="#DCEBFB" stroke-width="3" stroke-linecap="round"/>
<rect x="32" y="58" width="36" height="10" fill="#4F86C6"/>

</svg>
""",

    # ---- New "clip-art with label" style icons (milk / yogurt) ----

    "milk": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M30 90 L70 90 L70 40 L60 26 L50 18 L40 26 L30 40 Z" fill="#5B9BD5" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M50 18 L60 26 L70 40 L70 90 L60 90 L60 26 Z" fill="#3E7CB8" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<rect x="38" y="48" width="24" height="26" rx="2" fill="#FFFFFF" stroke="#1F2937" stroke-width="2.5"/>
<line x1="38" y1="61" x2="62" y2="61" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="59" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#1F2937" text-anchor="middle">MILK</text>
</svg>
""",

    "yogurt": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M30 40 L34 84 Q34 90 42 90 L58 90 Q66 90 66 84 L70 40 Z" fill="#BFE8E8" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<ellipse cx="50" cy="40" rx="20" ry="7" fill="#DFF5F5" stroke="#1F2937" stroke-width="3"/>
<path d="M62 34 Q70 34 70 40 Q70 46 62 44 Z" fill="#DFF5F5" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<rect x="32" y="52" width="36" height="16" fill="#EAF9F9" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="64" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#1F2937" text-anchor="middle">YOGURT</text>
</svg>
""",

    "hot_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#7C93C9"/>

<path d="M28,90 L72,90 L100,100 Z" fill="#000000" opacity="0.16"/>
<ellipse cx="50" cy="82" rx="30" ry="6" fill="#4338CA" opacity="0.5"/>
<path d="M30 48 L70 48 L65 78 L35 78Z" fill="#6D5AF0"/>
<path d="M50 48 L70 48 L65 78 L50 78Z" fill="#4338CA"/>
<ellipse cx="50" cy="48" rx="20" ry="5" fill="#4338CA"/>
<path d="M70 54 Q82 54 82 64 Q82 74 70 72" fill="none" stroke="#6D5AF0" stroke-width="5" stroke-linecap="round"/>
<path d="M40 38 Q44 32 40 26" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.8"/>
<path d="M58 38 Q62 32 58 26" fill="none" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" opacity="0.8"/>

</svg>
""",

    "cold_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#94A3AE"/>

<path d="M34,90 L66,90 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M44 14 L56 14 L56 24 L60 30 Q64 40 56 48 Q60 56 60 66 L60 84 Q60 90 52 90 L48 90 Q40 90 40 84 L40 66 Q40 56 44 48 Q36 40 40 30 Z" fill="#22A360"/>
<path d="M50 14 L56 14 L56 24 L60 30 Q64 40 56 48 Q60 56 60 66 L60 84 Q60 90 52 90 L50 90Z" fill="#186B3E"/>
<rect x="42" y="58" width="16" height="20" rx="2" fill="#FFFFFF" opacity="0.85"/>

</svg>
""",

    "sweet_snack": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8B84B"/>

<path d="M22,82 L78,82 L100,100 Z" fill="#000000" opacity="0.16"/>
<circle cx="50" cy="52" r="30" fill="#C99A63"/>
<path d="M50 22 A30 30 0 0 1 80 52 A30 30 0 0 1 62 79 Z" fill="#9C7742" opacity="0.55"/>
<circle cx="40" cy="44" r="3.4" fill="#5A3A22"/>
<circle cx="58" cy="42" r="3.4" fill="#5A3A22"/>
<circle cx="50" cy="56" r="3.4" fill="#5A3A22"/>
<circle cx="62" cy="60" r="3.4" fill="#5A3A22"/>

</svg>
""",

    # ---- New "clip-art with label" style icon (chips) ----

    "chips": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M28 22 Q50 14 72 22 L78 30 Q82 55 76 80 Q74 90 62 90 L38 90 Q26 90 24 80 Q18 55 22 30 Z" fill="#9DB8D9" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M28 22 Q50 14 72 22 L74 28 Q50 20 26 28 Z" fill="#6E93C4" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M24 80 Q50 88 76 80 L74 86 Q50 92 26 86 Z" fill="#6E93C4" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<text x="50" y="45" font-family="Arial, Helvetica, sans-serif" font-size="13" font-weight="800" fill="#2C4A73" text-anchor="middle">CHIPS</text>
<ellipse cx="50" cy="63" rx="14" ry="9" fill="#F4C15C" stroke="#1F2937" stroke-width="2"/>
</svg>
""",

    "noodles": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#9FB768"/>

<path d="M20,88 L80,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M22 56 Q50 44 78 56 L71 84 Q50 92 29 84Z" fill="#FFFFFF"/>
<ellipse cx="50" cy="56" rx="28" ry="10" fill="#F4C15C"/>
<path d="M32 56 Q40 46 48 56 Q56 66 64 56 Q70 48 76 56" fill="none" stroke="#D99A2B" stroke-width="3"/>
<circle cx="45" cy="52" r="2.6" fill="#E11D48"/>
<circle cx="58" cy="55" r="2.6" fill="#2E7D4F"/>

</svg>
""",

    # ---- New "clip-art with label" style icon (bread) ----

    "bread": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<g transform="rotate(-20 50 50)">
<rect x="18" y="55" width="64" height="30" rx="6" fill="#4FC3E0" stroke="#1F2937" stroke-width="3"/>
<path d="M30 55 Q50 30 70 55 Z" fill="#C88A4E" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M70 55 L82 40 L82 55 L76 62 Z" fill="#4FC3E0" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<line x1="36" y1="42" x2="40" y2="54" stroke="#A8703C" stroke-width="2"/>
<line x1="46" y1="34" x2="48" y2="54" stroke="#A8703C" stroke-width="2"/>
<line x1="56" y1="34" x2="54" y2="54" stroke="#A8703C" stroke-width="2"/>
<line x1="64" y1="42" x2="60" y2="54" stroke="#A8703C" stroke-width="2"/>
<text x="50" y="75" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="800" fill="#FFFFFF" text-anchor="middle">BREAD</text>
</g>
</svg>
""",

    "egg": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#C9BFAE"/>

<path d="M20,86 L80,86 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="24" y="58" width="52" height="24" rx="4" fill="#F4C15C" opacity="0.5"/>
<ellipse cx="38" cy="60" rx="13" ry="17" fill="#FFFFFF"/>
<ellipse cx="63" cy="58" rx="13" ry="17" fill="#FFFFFF"/>
<ellipse cx="38" cy="60" rx="13" ry="17" fill="#F1EBFE" opacity="0.35"/>

</svg>
""",

    "vegetable": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#9FB768"/>

<path d="M24,86 L76,86 L100,100 Z" fill="#000000" opacity="0.16"/>
<circle cx="42" cy="58" r="20" fill="#FB7185"/>
<path d="M42 38 A20 20 0 0 1 62 58 A20 20 0 0 1 50 76Z" fill="#DB2E5C" opacity="0.5"/>
<path d="M42 38 Q37 28 46 24 Q43 32 49 36Z" fill="#2E7D4F"/>
<circle cx="68" cy="66" r="13" fill="#2E7D4F"/>

</svg>
""",

    "fruit": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#C9BFAE"/>

<path d="M26,86 L74,86 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M50 40 Q34 40 34 60 Q34 82 50 82 Q66 82 66 60 Q66 40 50 40Z" fill="#FB7185"/>
<path d="M50 40 Q58 40 63 48 A22 22 0 0 1 58 79 Z" fill="#DB2E5C" opacity="0.5"/>
<path d="M50 40 Q48 30 52 24" fill="none" stroke="#8A5A34" stroke-width="3" stroke-linecap="round"/>
<path d="M52 26 Q58 22 64 26" fill="#2E7D4F"/>

</svg>
""",

    "spice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8B84B"/>

<path d="M28,88 L72,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<ellipse cx="50" cy="82" rx="22" ry="6" fill="#EA7C1F" opacity="0.4"/>
<rect x="30" y="42" width="40" height="40" rx="20" fill="#FDBA74"/>
<rect x="50" y="42" width="20" height="40" rx="20" fill="#EA7C1F"/>
<ellipse cx="50" cy="42" rx="20" ry="7" fill="#2E7D4F"/>
<path d="M44 24 Q50 34 56 24" fill="none" stroke="#2E7D4F" stroke-width="3" stroke-linecap="round"/>

</svg>
""",

    "personal_care": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8836E"/>

<path d="M26,86 L80,86 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="28" y="42" width="20" height="42" rx="6" fill="#FBCFE8"/>
<path d="M60 52 Q80 52 80 66 Q80 82 60 82 Q54 82 54 74 Q54 66 62 64 Q54 62 54 56 Q54 52 60 52Z" fill="#FFFFFF"/>
<rect x="63" y="42" width="8" height="12" rx="2" fill="#F472B6"/>

</svg>
""",

    "cleaning": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#3EB4C4"/>

<path d="M36,88 L64,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="38" y="40" width="24" height="46" rx="4" fill="#7DD3E8"/>
<rect x="50" y="40" width="12" height="46" rx="4" fill="#2A93B8"/>
<rect x="44" y="26" width="12" height="16" rx="2" fill="#2A93B8"/>
<path d="M56 30 L68 22" stroke="#2A93B8" stroke-width="3" stroke-linecap="round"/>

</svg>
""",

    "household": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#94A3AE"/>

<path d="M30,90 L70,90 L100,100 Z" fill="#000000" opacity="0.16"/>
<circle cx="50" cy="44" r="22" fill="#FDE68A"/>
<path d="M50 22 A22 22 0 0 1 68 62 Z" fill="#F4C15C" opacity="0.6"/>
<rect x="42" y="64" width="16" height="14" rx="3" fill="#3730A3"/>

</svg>
""",

    "pen": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#7C93C9"/>

<path d="M28,92 L72,92 L100,100 Z" fill="#000000" opacity="0.16"/>
<g transform="rotate(35 50 50)">
<rect x="42" y="12" width="16" height="52" rx="4" fill="#818CF8"/>
<rect x="50" y="12" width="8" height="52" fill="#4F46E5"/>
<path d="M42 64 L58 64 L50 80Z" fill="#3730A3"/>
<rect x="42" y="8" width="16" height="8" rx="3" fill="#3730A3"/>
</g>

</svg>
""",

    "notebook": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#C9BFAE"/>

<path d="M16,84 L80,84 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="28" y="20" width="46" height="60" rx="4" fill="#FFFFFF"/>
<rect x="18" y="20" width="12" height="60" rx="4" fill="#FB923C"/>
<line x1="38" y1="34" x2="66" y2="34" stroke="#E7E8F5" stroke-width="3"/>
<line x1="38" y1="46" x2="66" y2="46" stroke="#E7E8F5" stroke-width="3"/>
<line x1="38" y1="58" x2="60" y2="58" stroke="#E7E8F5" stroke-width="3"/>

</svg>
""",

    "medicine": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8836E"/>

<path d="M24,86 L76,86 L100,100 Z" fill="#000000" opacity="0.16"/>
<rect x="26" y="34" width="48" height="34" rx="6" fill="#FFFFFF"/>
<rect x="50" y="34" width="24" height="34" rx="6" fill="#F1EBFE"/>
<circle cx="38" cy="51" r="6" fill="#F472B6"/>
<circle cx="50" cy="51" r="6" fill="#818CF8"/>
<circle cx="62" cy="51" r="6" fill="#F472B6"/>

</svg>
""",

    "generic": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#7C93C9"/>

<path d="M16,68 L84,68 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M50 22 L82 38 L82 68 L50 84 L18 68 L18 38Z" fill="#A5B4FC"/>
<path d="M50 54 L82 38 L82 68 L50 84Z" fill="#6366F1" opacity="0.55"/>
<path d="M18 38 L50 54 L82 38" fill="none" stroke="#FFFFFF" stroke-width="2" opacity="0.4"/>
</svg>
""",
}

DEFAULT_TAG = "generic"

# ---------------------------------------------------------------------------
# Keyword -> tag matching (most specific first). Add more rows any time a
# new kind of product needs its own visual match.
# ---------------------------------------------------------------------------
_KEYWORD_TAGS = [
    ("basmati", "rice"), ("rice", "rice"),
    ("atta", "grain"), ("wheat", "grain"), ("flour", "grain"), ("besan", "grain"),
    ("poha", "grain"), ("suji", "grain"), ("rava", "grain"),
    ("dal", "grain"), ("pulses", "grain"),
    ("sugar", "sugar"),
    ("salt", "salt"),
    ("ghee", "bottle_oil"), ("oil", "bottle_oil"),
    ("milk", "milk"),
    ("curd", "yogurt"), ("yogurt", "yogurt"),
    ("paneer", "dairy"), ("butter", "dairy"), ("cheese", "dairy"),
    ("green tea", "hot_drink"), ("tea", "hot_drink"), ("coffee", "hot_drink"),
    ("juice", "cold_drink"), ("cold drink", "cold_drink"), ("soft drink", "cold_drink"),
    ("soda", "cold_drink"),
    ("water bottle", "cold_drink"), ("water", "cold_drink"),
    ("biscuit", "sweet_snack"), ("cookie", "sweet_snack"), ("chocolate", "sweet_snack"),
    ("candy", "sweet_snack"), ("ice cream", "sweet_snack"),
    ("chips", "chips"), ("namkeen", "chips"),
    ("noodles", "noodles"), ("maggi", "noodles"),
    ("bread", "bread"), ("bun", "bread"),
    ("egg", "egg"),
    ("onion", "vegetable"), ("potato", "vegetable"), ("tomato", "vegetable"),
    ("vegetable", "vegetable"),
    ("apple", "fruit"), ("banana", "fruit"), ("fruit", "fruit"),
    ("masala", "spice"), ("spice", "spice"), ("turmeric", "spice"),
    ("chilli", "spice"), ("chili", "spice"),
    ("soap", "personal_care"), ("shampoo", "personal_care"),
    ("toothpaste", "personal_care"), ("toothbrush", "personal_care"),
    ("hand wash", "personal_care"), ("sanitizer", "personal_care"),
    ("lotion", "personal_care"), ("razor", "personal_care"),
    ("perfume", "personal_care"), ("deodorant", "personal_care"),
    ("tissue", "personal_care"), ("napkin", "personal_care"), ("diaper", "personal_care"),
    ("detergent", "cleaning"), ("washing powder", "cleaning"), ("dishwash", "cleaning"),
    ("phenyl", "cleaning"), ("cleaner", "cleaning"), ("mop", "cleaning"), ("broom", "cleaning"),
    ("matchbox", "household"), ("candle", "household"), ("agarbatti", "household"),
    ("incense", "household"), ("bulb", "household"), ("battery", "household"),
    ("plastic bag", "household"),
    ("pen", "pen"), ("pencil", "pen"), ("marker", "pen"),
    ("notebook", "notebook"), ("eraser", "notebook"), ("stapler", "notebook"),
    ("envelope", "notebook"), ("paper", "notebook"),
    ("mask", "medicine"), ("bandage", "medicine"), ("medicine", "medicine"), ("syrup", "medicine"),
]

_CATEGORY_TAGS = {
    "grocery": "grain",
    "personal care": "personal_care",
    "snacks": "sweet_snack",
    "beverages": "cold_drink",
    "dairy": "milk",
    "bakery": "bread",
    "produce": "vegetable",
    "stationery": "notebook",
    "household": "cleaning",
    "health": "medicine",
}


def guess_image_tag(name: str, category: str = "") -> str:
    """Pick the best icon tag for this product: name keyword > category > generic."""
    n = (name or "").strip().lower()
    if n:
        for keyword, tag in _KEYWORD_TAGS:
            if re.search(r"\b" + re.escape(keyword) + r"\b", n):
                return tag

    c = (category or "").strip().lower()
    if c in _CATEGORY_TAGS:
        return _CATEGORY_TAGS[c]
    for cat_key, tag in _CATEGORY_TAGS.items():
        if cat_key in c:
            return tag

    return DEFAULT_TAG


@lru_cache(maxsize=64)
def _data_uri(tag: str) -> str:
    svg = ICON_SVGS.get(tag, ICON_SVGS[DEFAULT_TAG]).strip()
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def get_icon_data_uri(image_value):
    """
    Resolve a value stored in products.image_url into something a browser can
    actually display:
      - None / blank            -> None (caller shows the placeholder icon)
      - "icon:<tag>"             -> a bundled illustration, as a base64 SVG
                                     data URI
      - anything else (a real
        http(s) URL) -> returned unchanged
    """
    if not image_value:
        return None
    image_value = str(image_value).strip()
    if image_value.startswith("icon:"):
        tag = image_value.split(":", 1)[1] or DEFAULT_TAG
        return _data_uri(tag)
    return image_value


def is_auto_icon(image_value) -> bool:
    """True if this value is one of our auto-picked icons (not a real URL —
    typed in by a shopkeeper, or approved through photo review) — used to
    decide what to show in the 'Photo URL' edit box."""
    return bool(image_value) and str(image_value).strip().startswith("icon:")


def is_live_photo(image_value) -> bool:
    """
    True if this value is a real http(s) photo URL rather than one of our
    bundled 'icon:<tag>' illustrations or a blank/None value. Used to spot
    products currently showing a real (possibly wrong) web photo — either
    approved through the review flow, or left over from before that gate
    existed — so the shopkeeper can be offered a one-click way to reset
    them back to the safe drawn icon.
    """
    if not image_value:
        return False
    val = str(image_value).strip()
    return val.startswith("http://") or val.startswith("https://")
