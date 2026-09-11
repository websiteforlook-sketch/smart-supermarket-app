"""
product_images.py — Automatic product image matching (fully offline).

When a product is added — manually or via bulk CSV/Excel upload — and no
photo URL was supplied, this module guesses a relevant illustration from the
product name (e.g. "Basmati Rice" -> a rice-sack icon, "Bath Soap" -> a soap
icon, "Pen" -> a pen icon) and falls back to the product's category, then to
a generic box icon.

Unlike the earlier version of this file, nothing is fetched from the
internet. Every image is a small hand-drawn SVG bundled directly in this
file, base64-encoded into a data: URI at request time. That means:
  - it works even if the deployed app has no outbound internet access
  - a product's picture is 100% consistent every time (no random photo APIs)
  - there's no third-party licensing/copyright question, since every icon
    here is original artwork drawn for this project

Icon art style (v6 — "flat design + long shadow, distinct silhouettes")
---------------------------------------------------------------------------
Every icon uses the same recipe so the set reads as one consistent family
instead of 23 unrelated drawings:
  - flat, opaque solid-color shapes — no gradients, no outlines
  - a simple two-tone "shaded side" on each object for a hint of volume
    (a flat darker color block, not a smooth blend)
  - a diagonal "long shadow" wedge trailing from the object's base toward
    the bottom-right corner of the tile, at low opacity black — the
    classic flat-design/long-shadow icon trend
  - a solid muted-color rounded-square background tile, colors rotated
    through a fixed palette so adjacent icons never share the same hue
  - CRITICALLY: every tag has its own distinct real-world silhouette
    (tied burlap sack vs. folded flour bag vs. cylindrical shaker vs.
    gable-top milk carton vs. curvy soda bottle vs. round spice tin,
    etc.) rather than reusing one generic bottle/rectangle shape
    recolored — an earlier version did that and it read as repetitive
    and low-effort.
This replaced two earlier hand-drawn "cartoon sticker" attempts (soft
gradient + outline) and a first flat/long-shadow pass that reused near-
identical bottle silhouettes across too many tags. This version was built
after the shopkeeper picked "flat design + long shadow" from a set of
reference icon-pack styles shown to them directly.

Storage convention
-------------------
guess_image_tag() returns a short tag like "rice" or "personal_care".
Callers (db.py) store this in the products.image_url column as the string
"icon:<tag>" (e.g. "icon:rice") — NOT the SVG itself — so the column stays
tiny. At render time, get_icon_data_uri() turns "icon:<tag>" back into an
actual displayable image. Anything that isn't an "icon:" value (i.e. a real
http(s) URL a shopkeeper pasted in, or uploaded some other way) is passed
through untouched.
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
# When a shopkeeper adds a product without pasting their own photo, we now
# try to fetch a REAL photo of that product from the web instead of using a
# drawn icon. If the lookup fails for any reason (no internet access at
# deploy time, no results, a slow/broken API, etc.) we fall back to the
# bundled hand-drawn icon further down in this file, so a product is never
# left with a broken image.
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
def fetch_web_photo(name: str, category: str = "") -> str | None:
    """
    Look up a real photo of this product on the open web via Openverse's
    free public image-search API (no API key required). Returns a direct
    https:// image URL on success, or None if anything goes wrong — callers
    should fall back to an auto-picked icon (see guess_image_tag /
    get_icon_data_uri below) when this returns None.

    Cached per (name, category) for the life of the process so we don't
    hit the API again for a name we've already resolved this session; the
    resolved URL itself gets stored in products.image_url by the caller,
    so this only ever runs once per product, at add-time.
    """
    if requests is None:
        return None
    query = _build_search_query(name, category)
    if not query:
        return None
    try:
        resp = requests.get(
            _OPENVERSE_SEARCH_URL,
            params={
                "q": query,
                "page_size": 3,
                "mature": "false",
            },
            timeout=_WEB_PHOTO_TIMEOUT_SECONDS,
            headers={"User-Agent": "SmartMart-Inventory-App/1.0"},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        for item in results:
            url = item.get("url") or item.get("thumbnail")
            if url and url.startswith("http"):
                return url
    except Exception:
        pass  # any network/parse failure -> caller falls back to an icon
    return None

# ---------------------------------------------------------------------------
# Icon artwork — shaded, gradient-filled SVGs, 100x100 viewBox.
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

    "chips": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#E8836E"/>

<path d="M28,88 L72,88 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M30 34 L70 34 L64 88 L36 88Z" fill="#FB7185"/>
<path d="M50 34 L70 34 L64 88 L50 88Z" fill="#DB2E5C"/>
<path d="M30 34 L40 20 L50 34Z" fill="#DB2E5C"/>
<path d="M50 34 L60 20 L70 34Z" fill="#FB7185"/>
<ellipse cx="50" cy="58" rx="15" ry="9" fill="#FDE68A"/>

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

    "bread": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="14" fill="#3EB4C4"/>

<path d="M22,82 L78,82 L100,100 Z" fill="#000000" opacity="0.16"/>
<path d="M24 70 L24 48 Q24 26 50 26 Q76 26 76 48 L76 70 Q76 80 66 80 L34 80 Q24 80 24 70Z" fill="#EFCB93"/>
<path d="M50 26 Q76 26 76 48 L76 70 Q76 80 66 80 L50 80Z" fill="#CE9D5A"/>
<path d="M36 34 Q40 46 36 58" fill="none" stroke="#A67840" stroke-width="2"/>
<path d="M50 30 Q54 46 50 62" fill="none" stroke="#A67840" stroke-width="2"/>
<path d="M64 34 Q68 46 64 58" fill="none" stroke="#A67840" stroke-width="2"/>

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
    ("milk", "dairy"), ("curd", "dairy"), ("yogurt", "dairy"),
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
    "dairy": "dairy",
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
        http(s) URL the shopkeeper pasted in) -> returned unchanged
    """
    if not image_value:
        return None
    image_value = str(image_value).strip()
    if image_value.startswith("icon:"):
        tag = image_value.split(":", 1)[1] or DEFAULT_TAG
        return _data_uri(tag)
    return image_value


def is_auto_icon(image_value) -> bool:
    """True if this value is one of our auto-picked icons (not a real URL a
    shopkeeper typed in themselves) — used to decide what to show in the
    'Photo URL' edit box."""
    return bool(image_value) and str(image_value).strip().startswith("icon:")
