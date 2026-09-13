"""
product_images.py — Automatic product image matching.

Every product gets a bundled hand-drawn SVG icon, matched from the product
name/category — 100% offline, instant, and consistent no matter what the
product is. There is no web-photo lookup: an earlier version of this app
offered a "Review real photos" flow backed by a free openly-licensed image
search, but keyword search too often returned something irrelevant (a
landscape for "sunflower oil", an old advertisement scan for "soap"), so
that path has been removed entirely — every product now always shows one
of the drawn icons below.

Storage convention
-------------------
guess_image_tag() returns a short tag like "rice" or "personal_care".
Callers (db.py) store this in the products.image_url column as the string
"icon:<tag>" (e.g. "icon:rice") — NOT the SVG itself — so the column stays
tiny. At render time, get_icon_data_uri() turns "icon:<tag>" back into an
actual displayable image. A shopkeeper can still paste their own photo URL
into the "Photo URL" field on a product if they want to override the icon —
see is_live_photo() below, which is used to spot and optionally reset those.

Icon art style — "bold outline clip-art"
------------------------------------------
Every icon below shares one consistent visual language:
  - transparent background (no colored rounded square behind it)
  - thick dark outline (#1F2937, stroke-width 2.5–3)
  - flat, simplified color fills — no gradients or drop shadows
  - the product name baked in as a bold, readable text label, the same
    way a shelf sticker or packaging front would read
"""

import base64
import re
from functools import lru_cache

# ---------------------------------------------------------------------------
# Icon artwork — all tags share one "bold outline clip-art with a text
# label" style (see module docstring). Every icon is drawn on a transparent
# 100x100 canvas with a thick #1F2937 outline and a baked-in name label.
# ---------------------------------------------------------------------------

ICON_SVGS = {
    "rice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M32 34 Q30 20 50 18 Q70 20 68 34 L74 40 Q80 56 76 78 Q74 90 60 90 L40 90 Q26 90 24 78 Q20 56 26 40 Z" fill="#E8C77E" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M50 18 Q60 20 62 30" fill="none" stroke="#1F2937" stroke-width="2" stroke-linecap="round" opacity="0.35"/>
<ellipse cx="50" cy="34" rx="16" ry="5" fill="#D4A85C" stroke="#1F2937" stroke-width="2.5"/>
<rect x="30" y="55" width="40" height="18" rx="2" fill="#FFF8E7" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="68" font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="800" fill="#1F2937" text-anchor="middle">RICE</text>
</svg>
""",

    "grain": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M32 34 Q30 20 50 18 Q70 20 68 34 L74 40 Q80 56 76 78 Q74 90 60 90 L40 90 Q26 90 24 78 Q20 56 26 40 Z" fill="#D9A55C" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<ellipse cx="50" cy="34" rx="16" ry="5" fill="#B9843C" stroke="#1F2937" stroke-width="2.5"/>
<rect x="28" y="55" width="44" height="18" rx="2" fill="#FFF3DD" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="68" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="800" fill="#1F2937" text-anchor="middle">ATTA</text>
</svg>
""",

    "sugar": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M34 32 Q32 20 50 18 Q68 20 66 32 L72 40 Q78 56 74 78 Q72 90 58 90 L42 90 Q28 90 26 78 Q22 56 28 40 Z" fill="#FFFFFF" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<ellipse cx="50" cy="32" rx="15" ry="5" fill="#EEF0F5" stroke="#1F2937" stroke-width="2.5"/>
<rect x="30" y="54" width="40" height="18" rx="2" fill="#FDEEF6" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="67" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#1F2937" text-anchor="middle">SUGAR</text>
</svg>
""",

    "salt": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="34" y="36" width="32" height="52" rx="6" fill="#FFFFFF" stroke="#1F2937" stroke-width="3"/>
<ellipse cx="50" cy="30" rx="18" ry="8" fill="#2A93B8" stroke="#1F2937" stroke-width="3"/>
<rect x="34" y="58" width="32" height="16" fill="#DCEFF3" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="69" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">SALT</text>
</svg>
""",

    "bottle_oil": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="42" y="14" width="16" height="12" rx="2" fill="#C99A2B" stroke="#1F2937" stroke-width="2.5"/>
<path d="M38 26 L62 26 L68 42 L68 84 Q68 90 60 90 L40 90 Q32 90 32 84 L32 42 Z" fill="#F4C15C" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<rect x="38" y="52" width="24" height="22" rx="2" fill="#FFF9EC" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="66" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="800" fill="#1F2937" text-anchor="middle">OIL</text>
</svg>
""",

    "dairy": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="26" y="42" width="48" height="40" rx="4" fill="#FFF6D9" stroke="#1F2937" stroke-width="3"/>
<path d="M26 42 L36 30 L84 30 L74 42 Z" fill="#FFEBB0" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<path d="M74 42 L84 30 L84 70 L74 82 Z" fill="#F5DE8E" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<text x="49" y="67" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">PANEER</text>
</svg>
""",

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
<rect x="30" y="52" width="40" height="16" fill="#EAF9F9" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="64" font-family="Arial, Helvetica, sans-serif" font-size="8" font-weight="800" fill="#1F2937" text-anchor="middle">YOGURT</text>
</svg>
""",

    "hot_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M28 46 L72 46 L67 82 Q66 90 56 90 L44 90 Q34 90 33 82 Z" fill="#8B5E3C" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<ellipse cx="50" cy="46" rx="22" ry="6" fill="#6E4526" stroke="#1F2937" stroke-width="3"/>
<path d="M72 52 Q86 52 86 64 Q86 76 72 74" fill="none" stroke="#1F2937" stroke-width="4" stroke-linecap="round"/>
<path d="M40 36 Q44 28 40 20" fill="none" stroke="#1F2937" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>
<path d="M58 36 Q62 28 58 20" fill="none" stroke="#1F2937" stroke-width="2.5" stroke-linecap="round" opacity="0.5"/>
<text x="50" y="70" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#FFF6E9" text-anchor="middle">TEA</text>
</svg>
""",

    "cold_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M44 14 L56 14 L56 26 L62 34 Q66 44 58 50 Q64 58 64 68 L64 84 Q64 90 56 90 L44 90 Q36 90 36 84 L36 68 Q36 58 42 50 Q34 44 38 34 Z" fill="#3EBE7C" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<rect x="38" y="60" width="24" height="20" rx="2" fill="#FFFFFF" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="73" font-family="Arial, Helvetica, sans-serif" font-size="7" font-weight="800" fill="#1F2937" text-anchor="middle">COLD</text>
</svg>
""",

    "sweet_snack": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="20" y="34" width="60" height="40" rx="6" fill="#8B5E3C" stroke="#1F2937" stroke-width="3"/>
<line x1="35" y1="34" x2="35" y2="74" stroke="#1F2937" stroke-width="2.5"/>
<line x1="50" y1="34" x2="50" y2="74" stroke="#1F2937" stroke-width="2.5"/>
<line x1="65" y1="34" x2="65" y2="74" stroke="#1F2937" stroke-width="2.5"/>
<rect x="20" y="18" width="60" height="16" rx="4" fill="#F4C15C" stroke="#1F2937" stroke-width="3"/>
<text x="50" y="30" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">SNACKS</text>
</svg>
""",

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
<rect x="24" y="26" width="52" height="60" rx="6" fill="#F4C15C" stroke="#1F2937" stroke-width="3"/>
<ellipse cx="50" cy="58" rx="20" ry="12" fill="#FFFFFF" stroke="#1F2937" stroke-width="2.5"/>
<path d="M34 58 Q42 48 50 58 Q58 68 66 58" fill="none" stroke="#D99A2B" stroke-width="3"/>
<text x="50" y="38" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">NOODLES</text>
</svg>
""",

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
<rect x="18" y="40" width="64" height="42" rx="6" fill="#E8DCC4" stroke="#1F2937" stroke-width="3"/>
<path d="M18 40 L30 26 L70 26 L82 40 Z" fill="#F1E8D2" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<ellipse cx="34" cy="62" rx="10" ry="13" fill="#FFFFFF" stroke="#1F2937" stroke-width="2.5"/>
<ellipse cx="50" cy="62" rx="10" ry="13" fill="#FFFFFF" stroke="#1F2937" stroke-width="2.5"/>
<ellipse cx="66" cy="62" rx="10" ry="13" fill="#FFFFFF" stroke="#1F2937" stroke-width="2.5"/>
<text x="50" y="35" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">EGGS</text>
</svg>
""",

    "vegetable": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="54" r="26" fill="#EF6B5A" stroke="#1F2937" stroke-width="3"/>
<path d="M50 54 A26 26 0 0 1 70 72" fill="none" stroke="#C94A3C" stroke-width="2" opacity="0.5"/>
<path d="M42 30 Q38 20 48 18 Q46 26 50 30 Q54 26 52 18 Q62 20 58 30" fill="#2E7D4F" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<text x="50" y="92" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">VEGGIES</text>
</svg>
""",

    "fruit": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M50 32 Q34 32 32 52 Q30 76 44 84 Q47 86 50 84 Q53 86 56 84 Q70 76 68 52 Q66 32 50 32Z" fill="#E8483E" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M50 32 Q58 32 62 40 A22 22 0 0 1 58 80" fill="#C4362D" opacity="0.35"/>
<path d="M50 32 Q48 22 52 16" fill="none" stroke="#1F2937" stroke-width="3" stroke-linecap="round"/>
<path d="M52 18 Q60 14 66 20" fill="#2E7D4F" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
<text x="50" y="94" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#1F2937" text-anchor="middle">FRUIT</text>
</svg>
""",

    "spice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="32" y="40" width="36" height="46" rx="8" fill="#F4A83C" stroke="#1F2937" stroke-width="3"/>
<rect x="40" y="24" width="20" height="18" rx="4" fill="#8B5E3C" stroke="#1F2937" stroke-width="2.5"/>
<rect x="30" y="58" width="40" height="18" fill="#FFF3DD" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="70" font-family="Arial, Helvetica, sans-serif" font-size="7" font-weight="800" fill="#1F2937" text-anchor="middle">MASALA</text>
</svg>
""",

    "personal_care": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="20" y="38" width="60" height="34" rx="16" fill="#F9C6D8" stroke="#1F2937" stroke-width="3"/>
<ellipse cx="35" cy="50" rx="8" ry="5" fill="#FFFFFF" opacity="0.6"/>
<text x="50" y="59" font-family="Arial, Helvetica, sans-serif" font-size="11" font-weight="800" fill="#1F2937" text-anchor="middle">SOAP</text>
</svg>
""",

    "cleaning": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="34" y="34" width="32" height="52" rx="6" fill="#7DD3E8" stroke="#1F2937" stroke-width="3"/>
<rect x="42" y="20" width="16" height="16" rx="3" fill="#2A93B8" stroke="#1F2937" stroke-width="2.5"/>
<rect x="38" y="54" width="24" height="20" fill="#FFFFFF" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="67" font-family="Arial, Helvetica, sans-serif" font-size="8" font-weight="800" fill="#1F2937" text-anchor="middle">CLEAN</text>
</svg>
""",

    "household": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<circle cx="50" cy="46" r="24" fill="#FDE68A" stroke="#1F2937" stroke-width="3"/>
<rect x="42" y="68" width="16" height="14" rx="3" fill="#94A3AE" stroke="#1F2937" stroke-width="2.5"/>
<line x1="44" y1="78" x2="56" y2="78" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="50" font-family="Arial, Helvetica, sans-serif" font-size="8" font-weight="800" fill="#1F2937" text-anchor="middle">HOME</text>
</svg>
""",

    "pen": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<g transform="rotate(35 50 50)">
<rect x="42" y="12" width="16" height="52" rx="4" fill="#818CF8" stroke="#1F2937" stroke-width="3"/>
<rect x="42" y="8" width="16" height="8" rx="3" fill="#3730A3" stroke="#1F2937" stroke-width="2.5"/>
<path d="M42 64 L58 64 L50 80Z" fill="#3730A3" stroke="#1F2937" stroke-width="2.5" stroke-linejoin="round"/>
</g>
<text x="50" y="94" font-family="Arial, Helvetica, sans-serif" font-size="10" font-weight="800" fill="#1F2937" text-anchor="middle">PEN</text>
</svg>
""",

    "notebook": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="28" y="18" width="46" height="64" rx="4" fill="#FFFFFF" stroke="#1F2937" stroke-width="3"/>
<rect x="18" y="18" width="12" height="64" rx="4" fill="#FB923C" stroke="#1F2937" stroke-width="3"/>
<line x1="38" y1="34" x2="66" y2="34" stroke="#1F2937" stroke-width="2" opacity="0.35"/>
<line x1="38" y1="46" x2="66" y2="46" stroke="#1F2937" stroke-width="2" opacity="0.35"/>
<text x="52" y="66" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">NOTES</text>
</svg>
""",

    "medicine": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<rect x="20" y="40" width="60" height="30" rx="4" fill="#FFFFFF" stroke="#1F2937" stroke-width="3"/>
<circle cx="32" cy="55" r="6" fill="#F472B6" stroke="#1F2937" stroke-width="2"/>
<circle cx="50" cy="55" r="6" fill="#818CF8" stroke="#1F2937" stroke-width="2"/>
<circle cx="68" cy="55" r="6" fill="#F472B6" stroke="#1F2937" stroke-width="2"/>
<text x="50" y="82" font-family="Arial, Helvetica, sans-serif" font-size="7" font-weight="800" fill="#1F2937" text-anchor="middle">MEDICINE</text>
</svg>
""",

    "generic": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<path d="M50 20 L82 36 L82 68 L50 84 L18 68 L18 36 Z" fill="#A5B4FC" stroke="#1F2937" stroke-width="3" stroke-linejoin="round"/>
<path d="M50 52 L82 36 L82 68 L50 84 Z" fill="#818CF8" opacity="0.55"/>
<path d="M18 36 L50 52 L82 36" fill="none" stroke="#1F2937" stroke-width="2.5"/>
<text x="50" y="46" font-family="Arial, Helvetica, sans-serif" font-size="9" font-weight="800" fill="#1F2937" text-anchor="middle">ITEM</text>
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
