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

# ---------------------------------------------------------------------------
# Icon artwork — simple, flat, single-color-family SVGs, 100x100 viewBox.
# ---------------------------------------------------------------------------

ICON_SVGS = {
    "rice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F2F6C9"/>
<path d="M30 30 L70 30 L78 82 Q78 90 68 90 L32 90 Q22 90 22 82 Z" fill="#E9D9A8" stroke="#B98F4E" stroke-width="2"/>
<path d="M34 30 Q50 12 66 30" fill="none" stroke="#B98F4E" stroke-width="4" stroke-linecap="round"/>
<circle cx="42" cy="52" r="3" fill="#FBF6E6"/>
<circle cx="54" cy="58" r="3" fill="#FBF6E6"/>
<circle cx="46" cy="68" r="3" fill="#FBF6E6"/>
<circle cx="60" cy="48" r="3" fill="#FBF6E6"/>
</svg>""",

    "grain": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F2F6C9"/>
<rect x="26" y="34" width="48" height="52" rx="6" fill="#F1E9CC" stroke="#B98F4E" stroke-width="2"/>
<path d="M50 18 L54 30 L46 30 Z" fill="#E2623B"/>
<path d="M42 30 Q50 20 58 30" fill="none" stroke="#B98F4E" stroke-width="3"/>
<line x1="36" y1="50" x2="64" y2="50" stroke="#B98F4E" stroke-width="2"/>
<line x1="36" y1="62" x2="64" y2="62" stroke="#B98F4E" stroke-width="2"/>
<line x1="36" y1="74" x2="56" y2="74" stroke="#B98F4E" stroke-width="2"/>
</svg>""",

    "sugar": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F2F6C9"/>
<path d="M32 28 L68 28 L74 88 L26 88 Z" fill="#FFFFFF" stroke="#143427" stroke-width="2"/>
<path d="M40 28 L44 16 L56 16 L60 28" fill="none" stroke="#143427" stroke-width="2"/>
<circle cx="42" cy="48" r="2.4" fill="#E2623B"/>
<circle cx="52" cy="54" r="2.4" fill="#E2623B"/>
<circle cx="60" cy="46" r="2.4" fill="#E2623B"/>
<circle cx="46" cy="64" r="2.4" fill="#E2623B"/>
<circle cx="58" cy="68" r="2.4" fill="#E2623B"/>
</svg>""",

    "salt": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F2F6C9"/>
<path d="M35 30 Q50 22 65 30 L68 82 Q68 90 58 90 L42 90 Q32 90 32 82 Z" fill="#DCEFFB" stroke="#1E4A38" stroke-width="2"/>
<ellipse cx="50" cy="30" rx="15" ry="6" fill="#FFFFFF" stroke="#1E4A38" stroke-width="2"/>
<circle cx="44" cy="55" r="2" fill="#1E4A38"/>
<circle cx="52" cy="60" r="2" fill="#1E4A38"/>
<circle cx="58" cy="52" r="2" fill="#1E4A38"/>
<circle cx="47" cy="70" r="2" fill="#1E4A38"/>
</svg>""",

    "bottle_oil": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBF6E6"/>
<rect x="42" y="16" width="16" height="12" rx="2" fill="#B98F4E"/>
<path d="M38 28 L62 28 L68 42 L68 84 Q68 90 60 90 L40 90 Q32 90 32 84 L32 42 Z" fill="#E2A93B" stroke="#B98F4E" stroke-width="2"/>
<rect x="38" y="52" width="24" height="20" rx="3" fill="#FBF6E6" opacity="0.85"/>
</svg>""",

    "dairy": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#DCEFFB"/>
<path d="M36 22 L64 22 L64 34 L74 46 L74 86 Q74 90 70 90 L30 90 Q26 90 26 86 L26 46 L36 34 Z" fill="#FFFFFF" stroke="#1E4A38" stroke-width="2"/>
<rect x="26" y="52" width="48" height="14" fill="#2E7D4F"/>
<line x1="36" y1="22" x2="36" y2="34" stroke="#1E4A38" stroke-width="2"/>
<line x1="64" y1="22" x2="64" y2="34" stroke="#1E4A38" stroke-width="2"/>
</svg>""",

    "hot_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<path d="M30 40 L70 40 L66 82 Q65 88 58 88 L42 88 Q35 88 34 82 Z" fill="#8A5A34"/>
<path d="M70 46 Q84 46 84 58 Q84 70 70 68" fill="none" stroke="#8A5A34" stroke-width="5"/>
<path d="M40 30 Q44 24 40 18" fill="none" stroke="#B98F4E" stroke-width="3" stroke-linecap="round"/>
<path d="M52 30 Q56 24 52 18" fill="none" stroke="#B98F4E" stroke-width="3" stroke-linecap="round"/>
<path d="M64 30 Q68 24 64 18" fill="none" stroke="#B98F4E" stroke-width="3" stroke-linecap="round"/>
</svg>""",

    "cold_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBEFE7"/>
<rect x="44" y="14" width="12" height="10" rx="2" fill="#143427"/>
<path d="M38 24 L62 24 L66 36 L66 86 Q66 90 60 90 L40 90 Q34 90 34 86 L34 36 Z" fill="#E2623B" stroke="#B3432B" stroke-width="2"/>
<rect x="38" y="50" width="24" height="30" rx="3" fill="#FBF6E6" opacity="0.9"/>
</svg>""",

    "sweet_snack": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<circle cx="50" cy="52" r="30" fill="#C58A4E" stroke="#8A5A34" stroke-width="2"/>
<circle cx="40" cy="44" r="3.4" fill="#5A3A22"/>
<circle cx="58" cy="42" r="3.4" fill="#5A3A22"/>
<circle cx="50" cy="56" r="3.4" fill="#5A3A22"/>
<circle cx="62" cy="60" r="3.4" fill="#5A3A22"/>
<circle cx="38" cy="62" r="3.4" fill="#5A3A22"/>
</svg>""",

    "chips": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBEFE7"/>
<path d="M30 24 L70 24 L64 90 L36 90 Z" fill="#E2623B" stroke="#B3432B" stroke-width="2"/>
<path d="M38 24 L44 12 L56 12 L62 24" fill="none" stroke="#B3432B" stroke-width="2"/>
<ellipse cx="50" cy="55" rx="14" ry="8" fill="#F3A583"/>
</svg>""",

    "noodles": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<path d="M24 56 Q50 44 76 56 L70 84 Q50 92 30 84 Z" fill="#FFFFFF" stroke="#B98F4E" stroke-width="2"/>
<path d="M32 58 Q40 48 48 58 Q56 68 64 58 Q70 50 76 58" fill="none" stroke="#E2A93B" stroke-width="3"/>
<ellipse cx="50" cy="56" rx="26" ry="9" fill="#E9D9A8" stroke="#B98F4E" stroke-width="2"/>
</svg>""",

    "bread": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<path d="M24 70 L24 48 Q24 26 50 26 Q76 26 76 48 L76 70 Q76 80 66 80 L34 80 Q24 80 24 70 Z" fill="#E9C68C" stroke="#B98F4E" stroke-width="2"/>
<path d="M36 34 Q40 46 36 58" fill="none" stroke="#B98F4E" stroke-width="2"/>
<path d="M50 30 Q54 46 50 62" fill="none" stroke="#B98F4E" stroke-width="2"/>
<path d="M64 34 Q68 46 64 58" fill="none" stroke="#B98F4E" stroke-width="2"/>
</svg>""",

    "egg": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<rect x="24" y="52" width="52" height="30" rx="6" fill="#E9C68C" stroke="#B98F4E" stroke-width="2"/>
<ellipse cx="50" cy="42" rx="17" ry="22" fill="#FFFFFF" stroke="#B98F4E" stroke-width="2"/>
<circle cx="50" cy="44" r="7" fill="#E2A93B"/>
</svg>""",

    "vegetable": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#EAF3D8"/>
<circle cx="42" cy="58" r="20" fill="#E2623B" stroke="#B3432B" stroke-width="2"/>
<path d="M42 38 Q38 28 46 24 Q44 32 50 36" fill="#2E7D4F"/>
<circle cx="68" cy="66" r="13" fill="#2E7D4F"/>
<circle cx="68" cy="66" r="13" fill="none" stroke="#1E4A38" stroke-width="2"/>
</svg>""",

    "fruit": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBEFE7"/>
<path d="M50 40 Q34 40 34 60 Q34 82 50 82 Q66 82 66 60 Q66 40 50 40 Z" fill="#E2623B" stroke="#B3432B" stroke-width="2"/>
<path d="M50 40 Q48 30 52 24" fill="none" stroke="#8A5A34" stroke-width="3" stroke-linecap="round"/>
<path d="M52 26 Q58 22 64 26" fill="#2E7D4F"/>
</svg>""",

    "spice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBEFE7"/>
<path d="M28 56 Q50 40 72 56 L68 82 Q50 90 32 82 Z" fill="#E2623B" stroke="#B3432B" stroke-width="2"/>
<ellipse cx="50" cy="56" rx="22" ry="9" fill="#F3A583"/>
<path d="M44 24 Q50 34 56 24" fill="none" stroke="#2E7D4F" stroke-width="3" stroke-linecap="round"/>
</svg>""",

    "personal_care": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F8E7EE"/>
<rect x="30" y="40" width="18" height="44" rx="6" fill="#F2B8D0" stroke="#B3432B" stroke-width="2"/>
<rect x="35" y="30" width="8" height="12" rx="2" fill="#B3432B"/>
<path d="M58 50 Q76 50 76 66 Q76 82 58 82 Q52 82 52 74 Q52 66 60 64 Q52 62 52 56 Q52 50 58 50 Z" fill="#FFFFFF" stroke="#B3432B" stroke-width="2"/>
</svg>""",

    "cleaning": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#DCEFFB"/>
<rect x="38" y="40" width="24" height="46" rx="5" fill="#5FA8D3" stroke="#1E4A38" stroke-width="2"/>
<rect x="44" y="26" width="12" height="16" rx="2" fill="#1E4A38"/>
<path d="M56 30 L68 22" stroke="#1E4A38" stroke-width="3" stroke-linecap="round"/>
<path d="M64 18 L72 26 M72 18 L64 26" stroke="#1E4A38" stroke-width="2"/>
</svg>""",

    "household": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBF6E6"/>
<circle cx="50" cy="44" r="22" fill="#F3E38A" stroke="#B98F4E" stroke-width="2"/>
<rect x="42" y="64" width="16" height="14" rx="3" fill="#B98F4E"/>
<line x1="44" y1="82" x2="56" y2="82" stroke="#B98F4E" stroke-width="3" stroke-linecap="round"/>
<path d="M42 44 Q50 54 58 44" fill="none" stroke="#B98F4E" stroke-width="2"/>
</svg>""",

    "pen": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#DCEFFB"/>
<rect x="46" y="14" width="8" height="56" rx="3" transform="rotate(35 50 42)" fill="#1E4A38"/>
<path d="M62 62 L74 74 L66 80 L54 68 Z" fill="#5FA8D3" transform="rotate(35 50 42) translate(0,0)"/>
<path d="M30 78 L40 84 L34 90 Z" fill="#143427"/>
<rect x="20" y="70" width="26" height="10" rx="3" transform="rotate(35 50 42)" fill="#E2A93B"/>
</svg>""",

    "notebook": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<rect x="28" y="20" width="46" height="60" rx="4" fill="#FFFFFF" stroke="#B98F4E" stroke-width="2"/>
<rect x="20" y="20" width="10" height="60" rx="4" fill="#E2623B"/>
<circle cx="25" cy="30" r="2.4" fill="#FBF6E6"/>
<circle cx="25" cy="42" r="2.4" fill="#FBF6E6"/>
<circle cx="25" cy="54" r="2.4" fill="#FBF6E6"/>
<circle cx="25" cy="66" r="2.4" fill="#FBF6E6"/>
<line x1="38" y1="34" x2="66" y2="34" stroke="#E7DFC0" stroke-width="3"/>
<line x1="38" y1="46" x2="66" y2="46" stroke="#E7DFC0" stroke-width="3"/>
<line x1="38" y1="58" x2="60" y2="58" stroke="#E7DFC0" stroke-width="3"/>
</svg>""",

    "medicine": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#FBEFE7"/>
<rect x="26" y="34" width="48" height="34" rx="6" fill="#FFFFFF" stroke="#B3432B" stroke-width="2"/>
<circle cx="38" cy="51" r="6" fill="#F3A583"/>
<circle cx="50" cy="51" r="6" fill="#F3A583"/>
<circle cx="62" cy="51" r="6" fill="#F3A583"/>
<rect x="44" y="70" width="12" height="16" fill="#B3432B"/>
<rect x="38" y="76" width="24" height="4" fill="#B3432B"/>
</svg>""",

    "generic": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect width="100" height="100" rx="18" fill="#F1E9CC"/>
<path d="M50 22 L82 38 L82 68 L50 84 L18 68 L18 38 Z" fill="#E9C68C" stroke="#B98F4E" stroke-width="2"/>
<path d="M18 38 L50 54 L82 38" fill="none" stroke="#B98F4E" stroke-width="2"/>
<line x1="50" y1="54" x2="50" y2="84" stroke="#B98F4E" stroke-width="2"/>
</svg>""",
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
    ("juice", "cold_drink"), ("cold drink", "cold_drink"), ("soda", "cold_drink"),
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
