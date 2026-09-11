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

Icon art style (v2 — "shaded cartoon")
---------------------------------------
Every icon uses the same recipe so the set reads as one consistent family
instead of 23 unrelated drawings:
  - a soft gradient fill on the main object (not flat color) for a rounded,
    dimensional look
  - a single consistent deep-indigo ink outline (#3730A3) on every shape
  - a soft indigo drop-shadow ellipse under the object to ground it
  - a small white highlight ellipse/stroke for a glossy cartoon shine
  - background tile color drawn from the app's actual brand palette
    (amber / pink / indigo / teal / violet / emerald), grouped by product type
This was designed to sit next to the reference "flour / milk / butter"
illustration style the shopkeeper liked, adapted to the app's colors.

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
# Icon artwork — shaded, gradient-filled SVGs, 100x100 viewBox.
# ---------------------------------------------------------------------------

ICON_SVGS = {
    "rice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="riceSack" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#E9D9A8"/>
<stop offset="100%" stop-color="#CBAF74"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="90" rx="22" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M30 34 Q28 60 32 82 Q33 90 44 90 L58 90 Q68 90 69 82 Q71 58 68 34 Z" fill="url(#riceSack)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M30 34 Q50 42 68 34 Q50 26 30 34 Z" fill="#F6ECC9" stroke="#3730A3" stroke-width="2.5"/>
<path d="M36 34 Q50 20 62 34" fill="none" stroke="#3730A3" stroke-width="4" stroke-linecap="round"/>
<circle cx="44" cy="52" r="3" fill="#FBF6E6" stroke="#B8985B" stroke-width="0.5"/>
<circle cx="56" cy="58" r="3" fill="#FBF6E6" stroke="#B8985B" stroke-width="0.5"/>
<circle cx="48" cy="68" r="3" fill="#FBF6E6" stroke="#B8985B" stroke-width="0.5"/>
<circle cx="60" cy="48" r="3" fill="#FBF6E6" stroke="#B8985B" stroke-width="0.5"/>
<path d="M34 46 Q34 66 37 84" fill="none" stroke="#B8985B" stroke-width="1.5" opacity="0.5"/>
<ellipse cx="40" cy="42" rx="6" ry="10" fill="#FFFFFF" opacity="0.25"/>
</svg>""",

    "grain": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="flourSack" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#C99A63"/>
<stop offset="100%" stop-color="#A87844"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="90" rx="22" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M28 40 Q26 62 31 84 Q32 90 42 90 L58 90 Q68 90 69 84 Q74 62 72 40 Z" fill="url(#flourSack)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M34 40 Q50 30 66 40 Q50 48 34 40 Z" fill="#F3ECDD" stroke="#3730A3" stroke-width="2.5"/>
<path d="M40 30 Q50 18 60 30 Q52 32 50 40 Q48 32 40 30 Z" fill="#F3ECDD" stroke="#3730A3" stroke-width="2"/>
<path d="M38 40 Q34 60 38 82" fill="none" stroke="#8A6539" stroke-width="1.5" opacity="0.55"/>
<path d="M50 40 Q46 60 50 84" fill="none" stroke="#8A6539" stroke-width="1.5" opacity="0.55"/>
<path d="M62 40 Q66 60 62 82" fill="none" stroke="#8A6539" stroke-width="1.5" opacity="0.55"/>
<ellipse cx="38" cy="50" rx="6" ry="10" fill="#FFFFFF" opacity="0.2"/>
</svg>""",

    "sugar": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="sugarBag" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#EDEBF7"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="90" rx="20" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M33 32 L67 32 L72 84 Q72 90 64 90 L36 90 Q28 90 28 84 Z" fill="url(#sugarBag)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M40 32 L44 18 L56 18 L60 32" fill="none" stroke="#3730A3" stroke-width="2.5" stroke-linejoin="round"/>
<circle cx="42" cy="50" r="2.6" fill="#F472B6"/>
<circle cx="53" cy="56" r="2.6" fill="#818CF8"/>
<circle cx="61" cy="47" r="2.6" fill="#F472B6"/>
<circle cx="46" cy="66" r="2.6" fill="#818CF8"/>
<circle cx="58" cy="70" r="2.6" fill="#F472B6"/>
<ellipse cx="40" cy="42" rx="5" ry="9" fill="#FFFFFF" opacity="0.5"/>
</svg>""",

    "salt": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="saltBag" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#E8F7FB"/>
<stop offset="100%" stop-color="#C6E9F4"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#CFFAFE"/>
<ellipse cx="50" cy="90" rx="20" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M35 30 Q50 22 65 30 L69 82 Q69 90 59 90 L41 90 Q31 90 31 82 Z" fill="url(#saltBag)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="50" cy="30" rx="15" ry="6" fill="#FFFFFF" stroke="#3730A3" stroke-width="2.5"/>
<circle cx="44" cy="54" r="2.2" fill="#0EA5B7"/>
<circle cx="52" cy="60" r="2.2" fill="#0EA5B7"/>
<circle cx="58" cy="52" r="2.2" fill="#0EA5B7"/>
<circle cx="47" cy="70" r="2.2" fill="#0EA5B7"/>
<circle cx="56" cy="74" r="2.2" fill="#0EA5B7"/>
<ellipse cx="42" cy="42" rx="5" ry="9" fill="#FFFFFF" opacity="0.5"/>
</svg>""",

    "bottle_oil": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="oilBottle" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#F4C15C"/>
<stop offset="100%" stop-color="#D99A2B"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="92" rx="18" ry="4.5" fill="#3730A3" opacity="0.10"/>
<rect x="42" y="14" width="16" height="12" rx="2" fill="#3730A3"/>
<path d="M38 26 L62 26 L68 42 L68 84 Q68 90 60 90 L40 90 Q32 90 32 84 L32 42 Z" fill="url(#oilBottle)" stroke="#3730A3" stroke-width="2.5"/>
<rect x="38" y="50" width="24" height="22" rx="3" fill="#FFF9EC" opacity="0.92" stroke="#D99A2B" stroke-width="1"/>
<line x1="42" y1="57" x2="58" y2="57" stroke="#D99A2B" stroke-width="1.5"/>
<line x1="42" y1="63" x2="54" y2="63" stroke="#D99A2B" stroke-width="1.5"/>
<ellipse cx="40" cy="44" rx="4" ry="14" fill="#FFFFFF" opacity="0.35"/>
</svg>""",

    "dairy": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="milkCarton" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#DCEBFB"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#E0E7FF"/>
<ellipse cx="50" cy="91" rx="20" ry="4.5" fill="#3730A3" opacity="0.10"/>
<path d="M36 22 L64 22 L64 34 L74 46 L74 86 Q74 90 70 90 L30 90 Q26 90 26 86 L26 46 L36 34 Z" fill="url(#milkCarton)" stroke="#3730A3" stroke-width="2.5" stroke-linejoin="round"/>
<line x1="36" y1="22" x2="36" y2="34" stroke="#3730A3" stroke-width="2"/>
<line x1="64" y1="22" x2="64" y2="34" stroke="#3730A3" stroke-width="2"/>
<line x1="26" y1="46" x2="74" y2="46" stroke="#3730A3" stroke-width="2"/>
<rect x="26" y="54" width="48" height="13" fill="#4F86C6"/>
<circle cx="50" cy="60.5" r="6" fill="#FFFFFF" stroke="#3730A3" stroke-width="1.5"/>
<path d="M46 60.5 Q48 58 50 60.5 Q52 63 54 60.5" fill="none" stroke="#4F86C6" stroke-width="1.2"/>
<ellipse cx="34" cy="52" rx="4" ry="10" fill="#FFFFFF" opacity="0.5"/>
</svg>""",

    "hot_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="mugGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#6D5AF0"/>
<stop offset="100%" stop-color="#4338CA"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="88" rx="26" ry="5" fill="#3730A3" opacity="0.12"/>
<path d="M30 42 L70 42 L66 82 Q65 88 58 88 L42 88 Q35 88 34 82 Z" fill="url(#mugGrad)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="50" cy="42" rx="20" ry="5" fill="#8B7CF6"/>
<path d="M70 48 Q84 48 84 60 Q84 72 70 70" fill="none" stroke="#3730A3" stroke-width="5" stroke-linecap="round"/>
<path d="M40 32 Q44 26 40 20" fill="none" stroke="#3730A3" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<path d="M52 32 Q56 26 52 20" fill="none" stroke="#3730A3" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<path d="M64 32 Q68 26 64 20" fill="none" stroke="#3730A3" stroke-width="3" stroke-linecap="round" opacity="0.7"/>
<ellipse cx="42" cy="60" rx="4" ry="14" fill="#FFFFFF" opacity="0.18"/>
</svg>""",

    "cold_drink": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="coldBottle" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#FB7185"/>
<stop offset="100%" stop-color="#E11D48"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="92" rx="17" ry="4.5" fill="#3730A3" opacity="0.10"/>
<rect x="44" y="14" width="12" height="10" rx="2" fill="#3730A3"/>
<path d="M38 24 L62 24 L66 36 L66 86 Q66 90 60 90 L40 90 Q34 90 34 86 L34 36 Z" fill="url(#coldBottle)" stroke="#3730A3" stroke-width="2.5"/>
<rect x="38" y="50" width="24" height="26" rx="3" fill="#FFF5F7" opacity="0.92" stroke="#E11D48" stroke-width="1"/>
<circle cx="44" cy="60" r="2" fill="#FCA5C0"/>
<circle cx="52" cy="66" r="1.6" fill="#FCA5C0"/>
<circle cx="46" cy="70" r="1.4" fill="#FCA5C0"/>
<ellipse cx="40" cy="40" rx="4" ry="14" fill="#FFFFFF" opacity="0.4"/>
</svg>""",

    "sweet_snack": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="cookieGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#E3AE6E"/>
<stop offset="100%" stop-color="#B9803F"/>
</radialGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="90" rx="24" ry="5" fill="#3730A3" opacity="0.10"/>
<circle cx="50" cy="52" r="30" fill="url(#cookieGrad)" stroke="#3730A3" stroke-width="2.5"/>
<circle cx="40" cy="44" r="3.6" fill="#5A3A22"/>
<circle cx="58" cy="42" r="3.6" fill="#5A3A22"/>
<circle cx="50" cy="56" r="3.6" fill="#5A3A22"/>
<circle cx="62" cy="60" r="3.6" fill="#5A3A22"/>
<circle cx="38" cy="62" r="3.6" fill="#5A3A22"/>
<ellipse cx="40" cy="38" rx="8" ry="5" fill="#FFFFFF" opacity="0.3"/>
</svg>""",

    "chips": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="chipBag" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FB7185"/>
<stop offset="100%" stop-color="#DB2E5C"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="91" rx="20" ry="4.5" fill="#3730A3" opacity="0.10"/>
<path d="M30 24 L70 24 L64 88 L36 88 Z" fill="url(#chipBag)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M38 24 L44 12 L56 12 L62 24" fill="none" stroke="#3730A3" stroke-width="2.5" stroke-linejoin="round"/>
<ellipse cx="50" cy="55" rx="15" ry="9" fill="#FFE8A3" stroke="#B9803F" stroke-width="1.5"/>
<ellipse cx="46" cy="53" rx="3" ry="1.6" fill="#E3AE6E"/>
<ellipse cx="55" cy="58" rx="3" ry="1.6" fill="#E3AE6E"/>
<ellipse cx="38" cy="38" rx="4" ry="10" fill="#FFFFFF" opacity="0.3"/>
</svg>""",

    "noodles": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="bowlGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#E7E8F5"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="90" rx="26" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M22 56 Q50 44 78 56 L71 84 Q50 92 29 84 Z" fill="url(#bowlGrad)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="50" cy="56" rx="28" ry="10" fill="#F4C15C" stroke="#3730A3" stroke-width="2.5"/>
<path d="M32 56 Q40 46 48 56 Q56 66 64 56 Q70 48 76 56" fill="none" stroke="#B9803F" stroke-width="2.5"/>
<circle cx="45" cy="52" r="2.4" fill="#E11D48"/>
<circle cx="58" cy="55" r="2.4" fill="#2E7D4F"/>
<path d="M40 30 Q44 22 40 14" fill="none" stroke="#3730A3" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
<path d="M58 30 Q62 22 58 14" fill="none" stroke="#3730A3" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
</svg>""",

    "bread": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="breadGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#EFCB93"/>
<stop offset="100%" stop-color="#CE9D5A"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="88" rx="26" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M24 70 L24 48 Q24 26 50 26 Q76 26 76 48 L76 70 Q76 80 66 80 L34 80 Q24 80 24 70 Z" fill="url(#breadGrad)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M36 34 Q40 46 36 58" fill="none" stroke="#A67840" stroke-width="2"/>
<path d="M50 30 Q54 46 50 62" fill="none" stroke="#A67840" stroke-width="2"/>
<path d="M64 34 Q68 46 64 58" fill="none" stroke="#A67840" stroke-width="2"/>
<ellipse cx="36" cy="38" rx="6" ry="4" fill="#FFFFFF" opacity="0.3"/>
</svg>""",

    "egg": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="eggGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#F1EBFE"/>
</radialGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FEF3D6"/>
<ellipse cx="50" cy="88" rx="24" ry="5" fill="#3730A3" opacity="0.10"/>
<rect x="24" y="52" width="52" height="30" rx="6" fill="#E3AE6E" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="50" cy="42" rx="17" ry="22" fill="url(#eggGrad)" stroke="#3730A3" stroke-width="2.5"/>
<circle cx="50" cy="46" r="7" fill="#F4C15C" stroke="#D99A2B" stroke-width="1"/>
<ellipse cx="43" cy="34" rx="4" ry="7" fill="#FFFFFF" opacity="0.6"/>
</svg>""",

    "vegetable": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="tomatoGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#FB7185"/>
<stop offset="100%" stop-color="#DB2E5C"/>
</radialGradient>
<radialGradient id="cabGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#6EE7A8"/>
<stop offset="100%" stop-color="#22A360"/>
</radialGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#DCFCE9"/>
<ellipse cx="50" cy="88" rx="24" ry="5" fill="#3730A3" opacity="0.10"/>
<circle cx="40" cy="58" r="20" fill="url(#tomatoGrad)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M40 38 Q35 28 44 24 Q41 32 47 36" fill="#2E7D4F" stroke="#3730A3" stroke-width="1.5"/>
<ellipse cx="34" cy="50" rx="4" ry="6" fill="#FFFFFF" opacity="0.4"/>
<circle cx="68" cy="66" r="14" fill="url(#cabGrad)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="63" cy="60" rx="3" ry="4" fill="#FFFFFF" opacity="0.35"/>
</svg>""",

    "fruit": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="appleGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#FB7185"/>
<stop offset="100%" stop-color="#DB2E5C"/>
</radialGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="88" rx="20" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M50 40 Q34 40 34 60 Q34 82 50 82 Q66 82 66 60 Q66 40 50 40 Z" fill="url(#appleGrad)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M50 40 Q48 30 52 24" fill="none" stroke="#5A3A22" stroke-width="3" stroke-linecap="round"/>
<path d="M52 26 Q58 22 64 26" fill="#2E7D4F" stroke="#3730A3" stroke-width="1.5"/>
<ellipse cx="42" cy="52" rx="5" ry="9" fill="#FFFFFF" opacity="0.4"/>
</svg>""",

    "spice": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="spiceBowl" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FDBA74"/>
<stop offset="100%" stop-color="#EA7C1F"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="88" rx="24" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M28 56 Q50 42 72 56 L67 82 Q50 90 33 82 Z" fill="url(#spiceBowl)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="50" cy="56" rx="22" ry="9" fill="#FDD9AE" stroke="#3730A3" stroke-width="2"/>
<path d="M44 24 Q50 34 56 24" fill="none" stroke="#2E7D4F" stroke-width="3" stroke-linecap="round"/>
<circle cx="50" cy="20" r="3" fill="#2E7D4F"/>
</svg>""",

    "personal_care": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="soapGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FBCFE8"/>
<stop offset="100%" stop-color="#F472B6"/>
</linearGradient>
<linearGradient id="pumpGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#F1EBFE"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="90" rx="24" ry="5" fill="#3730A3" opacity="0.10"/>
<rect x="28" y="42" width="20" height="42" rx="7" fill="url(#soapGrad)" stroke="#3730A3" stroke-width="2.5"/>
<ellipse cx="38" cy="50" rx="6" ry="3" fill="#FFFFFF" opacity="0.5"/>
<path d="M60 52 Q80 52 80 66 Q80 82 60 82 Q54 82 54 74 Q54 66 62 64 Q54 62 54 56 Q54 52 60 52 Z" fill="url(#pumpGrad)" stroke="#3730A3" stroke-width="2.5"/>
<rect x="63" y="42" width="8" height="12" rx="2" fill="#3730A3"/>
</svg>""",

    "cleaning": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="sprayGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#7DD3E8"/>
<stop offset="100%" stop-color="#2A93B8"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#CFFAFE"/>
<ellipse cx="50" cy="90" rx="20" ry="5" fill="#3730A3" opacity="0.10"/>
<rect x="38" y="40" width="24" height="46" rx="5" fill="url(#sprayGrad)" stroke="#3730A3" stroke-width="2.5"/>
<rect x="44" y="26" width="12" height="16" rx="2" fill="#3730A3"/>
<path d="M56 30 L68 22" stroke="#3730A3" stroke-width="3" stroke-linecap="round"/>
<path d="M64 18 L72 26 M72 18 L64 26" stroke="#3730A3" stroke-width="2"/>
<rect x="42" y="56" width="16" height="20" rx="2" fill="#FFFFFF" opacity="0.5"/>
</svg>""",

    "household": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<radialGradient id="bulbGrad" cx="35%" cy="30%" r="75%">
<stop offset="0%" stop-color="#FDE68A"/>
<stop offset="100%" stop-color="#F4C15C"/>
</radialGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#F1EBFE"/>
<ellipse cx="50" cy="90" rx="20" ry="5" fill="#3730A3" opacity="0.10"/>
<circle cx="50" cy="44" r="22" fill="url(#bulbGrad)" stroke="#3730A3" stroke-width="2.5"/>
<rect x="42" y="64" width="16" height="14" rx="3" fill="#3730A3"/>
<line x1="44" y1="82" x2="56" y2="82" stroke="#3730A3" stroke-width="3" stroke-linecap="round"/>
<path d="M42 44 Q50 54 58 44" fill="none" stroke="#B9803F" stroke-width="2"/>
<ellipse cx="42" cy="36" rx="5" ry="7" fill="#FFFFFF" opacity="0.4"/>
</svg>""",

    "pen": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="penGrad" x1="0" y1="0" x2="1" y2="1">
<stop offset="0%" stop-color="#818CF8"/>
<stop offset="100%" stop-color="#4F46E5"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#E0E7FF"/>
<ellipse cx="50" cy="90" rx="22" ry="4.5" fill="#3730A3" opacity="0.10"/>
<g transform="rotate(35 50 50)">
<rect x="42" y="12" width="16" height="52" rx="4" fill="url(#penGrad)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M42 64 L58 64 L50 80 Z" fill="#3730A3"/>
<rect x="42" y="8" width="16" height="8" rx="3" fill="#3730A3"/>
<rect x="44" y="20" width="4" height="30" rx="2" fill="#FFFFFF" opacity="0.4"/>
</g>
</svg>""",

    "notebook": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="notebookGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FB923C"/>
<stop offset="100%" stop-color="#EA580C"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#F1EBFE"/>
<ellipse cx="50" cy="90" rx="24" ry="4.5" fill="#3730A3" opacity="0.10"/>
<rect x="28" y="20" width="46" height="60" rx="4" fill="#FFFFFF" stroke="#3730A3" stroke-width="2.5"/>
<rect x="18" y="20" width="12" height="60" rx="4" fill="url(#notebookGrad)" stroke="#3730A3" stroke-width="2.5"/>
<circle cx="24" cy="30" r="2.4" fill="#FBF6E6"/>
<circle cx="24" cy="42" r="2.4" fill="#FBF6E6"/>
<circle cx="24" cy="54" r="2.4" fill="#FBF6E6"/>
<circle cx="24" cy="66" r="2.4" fill="#FBF6E6"/>
<line x1="38" y1="34" x2="66" y2="34" stroke="#E7E8F5" stroke-width="3"/>
<line x1="38" y1="46" x2="66" y2="46" stroke="#E7E8F5" stroke-width="3"/>
<line x1="38" y1="58" x2="60" y2="58" stroke="#E7E8F5" stroke-width="3"/>
</svg>""",

    "medicine": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="medStrip" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#FFFFFF"/>
<stop offset="100%" stop-color="#F1EBFE"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#FCE7F3"/>
<ellipse cx="50" cy="90" rx="24" ry="4.5" fill="#3730A3" opacity="0.10"/>
<rect x="26" y="34" width="48" height="34" rx="6" fill="url(#medStrip)" stroke="#3730A3" stroke-width="2.5"/>
<circle cx="38" cy="51" r="6" fill="#F472B6" stroke="#DB2E5C" stroke-width="1"/>
<circle cx="50" cy="51" r="6" fill="#818CF8" stroke="#4F46E5" stroke-width="1"/>
<circle cx="62" cy="51" r="6" fill="#F472B6" stroke="#DB2E5C" stroke-width="1"/>
<rect x="44" y="70" width="12" height="16" fill="#3730A3"/>
<rect x="38" y="76" width="24" height="4" fill="#3730A3"/>
</svg>""",

    "generic": """
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="boxGrad" x1="0" y1="0" x2="0" y2="1">
<stop offset="0%" stop-color="#A5B4FC"/>
<stop offset="100%" stop-color="#6366F1"/>
</linearGradient>
</defs>
<rect width="100" height="100" rx="18" fill="#E0E7FF"/>
<ellipse cx="50" cy="88" rx="26" ry="5" fill="#3730A3" opacity="0.10"/>
<path d="M50 22 L82 38 L82 68 L50 84 L18 68 L18 38 Z" fill="url(#boxGrad)" stroke="#3730A3" stroke-width="2.5"/>
<path d="M18 38 L50 54 L82 38" fill="none" stroke="#3730A3" stroke-width="2"/>
<line x1="50" y1="54" x2="50" y2="84" stroke="#3730A3" stroke-width="2"/>
<path d="M34 30 L50 38 L66 30" fill="none" stroke="#FFFFFF" stroke-width="1.5" opacity="0.4"/>
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
