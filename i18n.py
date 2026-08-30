"""
i18n.py — Minimal English / Gujarati translation layer for SmartMart.

Usage:
    import i18n
    i18n.t("dashboard")            -> "Dashboard" or "ડેશબોર્ડ" depending on
                                       st.session_state.lang
    i18n.t("stock_updated", name="Rice", qty=15)
                                    -> fills in a template string in whichever
                                       language is active

render_lang_toggle() draws a small English/ગુજરાતી switcher. It's placed on
the auth screen (so a shopkeeper who can't read English can switch before
even logging in) and again in the sidebar once logged in.

Product data itself (names, categories the shopkeeper typed in) is never
translated — only the app's own UI chrome (labels, buttons, instructions).
"""

import streamlit as st

TRANSLATIONS = {
    # ---- Sidebar / nav ----
    "nav_dashboard": {"en": "Dashboard", "gu": "ડેશબોર્ડ"},
    "nav_products": {"en": "Products", "gu": "ઉત્પાદનો"},
    "nav_sales": {"en": "Sales", "gu": "વેચાણ"},
    "nav_reports": {"en": "Reports", "gu": "અહેવાલો"},
    "log_out": {"en": "↩ Log out", "gu": "↩ લોગ આઉટ"},
    "signed_in_as": {"en": "Signed in as {name}", "gu": "{name} તરીકે સાઇન ઇન"},

    # ---- Auth: shared ----
    "hero_eyebrow": {"en": "BUILT FOR SHOPS THAT MOVE FAST", "gu": "ઝડપી દુકાનો માટે બનાવેલ"},
    "hero_script": {"en": "Run your shop,", "gu": "તમારી દુકાન,"},
    "hero_caps": {"en": "like clockwork.", "gu": "ઘડિયાળની જેમ ચલાવો."},
    "hero_headline": {"en": "Run your shop<br/>like clockwork.",
                       "gu": "તમારી દુકાન<br/>ઘડિયાળની જેમ ચલાવો."},
    "hero_sub": {"en": "One dashboard for stock, sales, and barcodes — "
                       "built to feel as simple as writing it in a ledger.",
                 "gu": "સ્ટોક, વેચાણ અને બારકોડ માટે એક જ ડેશબોર્ડ — "
                       "ચોપડામાં લખવા જેટલું સરળ."},
    "feat_stock_title": {"en": "Live stock", "gu": "લાઇવ સ્ટોક"},
    "feat_stock_desc": {"en": "Know what's in and out, down to the unit.",
                         "gu": "શું અંદર-બહાર છે, ચોક્કસ સંખ્યામાં જાણો."},
    "feat_barcode_title": {"en": "Barcode ready", "gu": "બારકોડ તૈયાર"},
    "feat_barcode_desc": {"en": "Scan to restock or add new items in seconds.",
                           "gu": "થોડી સેકન્ડમાં સ્કેન કરી સ્ટોક ભરો અથવા નવી વસ્તુ ઉમેરો."},
    "feat_dash_title": {"en": "Clear dashboards", "gu": "સ્પષ્ટ ડેશબોર્ડ"},
    "feat_dash_desc": {"en": "See what's selling without digging for it.",
                        "gu": "શું વેચાઈ રહ્યું છે તે સહેલાઈથી જુઓ."},
    "feat_export_title": {"en": "Export anytime", "gu": "ગમે ત્યારે નિકાસ કરો"},
    "feat_export_desc": {"en": "A clean Excel report, whenever you need one.",
                          "gu": "જ્યારે જરૂર પડે ત્યારે સ્વચ્છ એક્સેલ રિપોર્ટ."},

    # ---- Auth: login ----
    "welcome_back": {"en": "Welcome back", "gu": "ફરી સ્વાગત છે"},
    "login_sub": {"en": "Log in to your shop dashboard.", "gu": "તમારા દુકાન ડેશબોર્ડમાં લોગ ઇન કરો."},
    "username": {"en": "Username", "gu": "વપરાશકર્તા નામ"},
    "password": {"en": "Password", "gu": "પાસવર્ડ"},
    "log_in": {"en": "Log in", "gu": "લોગ ઇન"},
    "forgot_password": {"en": "Forgot password?", "gu": "પાસવર્ડ ભૂલી ગયા?"},
    "create_account_link": {"en": "Create an account →", "gu": "ખાતું બનાવો →"},
    "fill_both_fields": {"en": "Enter both a username and password.",
                          "gu": "વપરાશકર્તા નામ અને પાસવર્ડ બંને દાખલ કરો."},
    "wrong_login": {"en": "Incorrect username or password.", "gu": "ખોટું વપરાશકર્તા નામ અથવા પાસવર્ડ."},

    # ---- Auth: signup ----
    "setup_shop": {"en": "Set up your shop", "gu": "તમારી દુકાન સેટ કરો"},
    "setup_sub": {"en": "Takes less than a minute.", "gu": "એક મિનિટથી પણ ઓછો સમય લાગે છે."},
    "shop_name": {"en": "Shop name", "gu": "દુકાનનું નામ"},
    "owner_name": {"en": "Shop owner name", "gu": "દુકાનમાલિકનું નામ"},
    "confirm_password": {"en": "Confirm password", "gu": "પાસવર્ડની પુષ્ટિ કરો"},
    "create_account": {"en": "Create account", "gu": "ખાતું બનાવો"},
    "back_to_login": {"en": "← Back to log in", "gu": "← લોગ ઇન પર પાછા"},
    "fill_all_fields": {"en": "Fill in all fields.", "gu": "બધા ફિલ્ડ ભરો."},
    "passwords_no_match": {"en": "Passwords don't match.", "gu": "પાસવર્ડ મેળ ખાતા નથી."},
    "password_too_short": {"en": "Password should be at least 4 characters.",
                            "gu": "પાસવર્ડ ઓછામાં ઓછો 4 અક્ષરોનો હોવો જોઈએ."},
    "welcome_toast": {"en": "Welcome, {shop}! Your shop is set up.",
                       "gu": "સ્વાગત છે, {shop}! તમારી દુકાન તૈયાર છે."},

    # ---- Auth: forgot password ----
    "reset_password_title": {"en": "Reset your password", "gu": "તમારો પાસવર્ડ રીસેટ કરો"},
    "reset_sub": {"en": "Enter your username and choose a new password.",
                  "gu": "તમારું વપરાશકર્તા નામ દાખલ કરો અને નવો પાસવર્ડ પસંદ કરો."},
    "new_password": {"en": "New password", "gu": "નવો પાસવર્ડ"},
    "confirm_new_password": {"en": "Confirm new password", "gu": "નવા પાસવર્ડની પુષ્ટિ કરો"},
    "update_password": {"en": "Update password", "gu": "પાસવર્ડ અપડેટ કરો"},
    "no_account_found": {"en": "No account found with that username.",
                          "gu": "આ વપરાશકર્તા નામ સાથે કોઈ ખાતું મળ્યું નથી."},

    # ---- Dashboard ----
    "good_morning": {"en": "Good morning", "gu": "સુપ્રભાત"},
    "good_afternoon": {"en": "Good afternoon", "gu": "શુભ બપોર"},
    "good_evening": {"en": "Good evening", "gu": "શુભ સાંજ"},
    "welcome_sub": {"en": "Here's how your shop is doing today.",
                    "gu": "આજે તમારી દુકાન કેવી ચાલી રહી છે તે અહીં છે."},
    "kpi_products": {"en": "Products tracked", "gu": "ટ્રેક કરેલા ઉત્પાદનો"},
    "kpi_products_sub": {"en": "across all categories", "gu": "બધી શ્રેણીઓમાં"},
    "kpi_stock_value": {"en": "Stock value", "gu": "સ્ટોકનું મૂલ્ય"},
    "kpi_stock_value_sub": {"en": "at current price × qty", "gu": "વર્તમાન કિંમત × જથ્થા પ્રમાણે"},
    "kpi_sales_today": {"en": "Sales today", "gu": "આજનું વેચાણ"},
    "kpi_low_stock": {"en": "Low stock alerts", "gu": "ઓછા સ્ટોકની ચેતવણી"},
    "kpi_low_stock_sub": {"en": "5 units or fewer", "gu": "5 કે તેથી ઓછા એકમો"},
    "top_selling": {"en": "Top-selling products", "gu": "સૌથી વધુ વેચાતા ઉત્પાદનો"},
    "stock_by_category": {"en": "Stock by category", "gu": "શ્રેણી પ્રમાણે સ્ટોક"},
    "low_stock_title": {"en": "Low stock — restock soon", "gu": "ઓછો સ્ટોક — ટૂંક સમયમાં ભરો"},
    "well_stocked": {"en": "Everything is well stocked.", "gu": "બધું સારી રીતે સ્ટોક કરેલું છે."},
    "no_sales_yet": {"en": "No sales recorded yet.", "gu": "હજુ કોઈ વેચાણ નોંધાયું નથી."},
    "no_products_yet": {"en": "No products yet.", "gu": "હજુ કોઈ ઉત્પાદન નથી."},
    "units_sold": {"en": "Units sold", "gu": "વેચાયેલા એકમો"},

    # ---- Products page ----
    "tab_add_manually": {"en": "➕ Add manually", "gu": "➕ જાતે ઉમેરો"},
    "tab_bulk_upload": {"en": "📄 Bulk upload", "gu": "📄 બલ્ક અપલોડ"},
    "tab_scan_barcode": {"en": "🔍 Scan barcode", "gu": "🔍 બારકોડ સ્કેન કરો"},
    "tab_all_products": {"en": "📋 All products", "gu": "📋 બધા ઉત્પાદનો"},
    "product_name": {"en": "Product name", "gu": "ઉત્પાદનનું નામ"},
    "category": {"en": "Category", "gu": "શ્રેણી"},
    "price_rs": {"en": "Price (₹)", "gu": "કિંમત (₹)"},
    "opening_stock": {"en": "Opening stock", "gu": "શરૂઆતનો સ્ટોક"},
    "barcode_optional": {"en": "Barcode (optional)", "gu": "બારકોડ (વૈકલ્પિક)"},
    "photo_url_optional": {"en": "Product photo URL (optional)", "gu": "ઉત્પાદનના ફોટાની URL (વૈકલ્પિક)"},
    "photo_url_help": {"en": "Paste a direct link to an image. Leave blank to show a placeholder icon.",
                        "gu": "ફોટાની સીધી લિંક પેસ્ટ કરો. ખાલી રાખશો તો પ્લેસહોલ્ડર આઇકોન દેખાશે."},
    "add_product": {"en": "Add product", "gu": "ઉત્પાદન ઉમેરો"},
    "name_required": {"en": "Product name is required.", "gu": "ઉત્પાદનનું નામ જરૂરી છે."},
    "bulk_instructions": {"en": "Upload a CSV or Excel file with columns: **name, category, price, "
                                 "stock, barcode, image_url** (barcode and image_url are optional; "
                                 "column names are matched case-insensitively).",
                           "gu": "આ કોલમ સાથે CSV અથવા Excel ફાઇલ અપલોડ કરો: **name, category, price, "
                                 "stock, barcode, image_url** (barcode અને image_url વૈકલ્પિક છે)."},
    "choose_file": {"en": "Choose file", "gu": "ફાઇલ પસંદ કરો"},
    "import_products": {"en": "Import these products", "gu": "આ ઉત્પાદનો આયાત કરો"},
    "imported_summary": {"en": "Imported {success} product(s). Skipped {skipped}.",
                          "gu": "{success} ઉત્પાદનો આયાત થયા. {skipped} છોડ્યા."},
    "see_skipped": {"en": "See skipped rows", "gu": "છોડેલી પંક્તિઓ જુઓ"},
    "file_read_error": {"en": "Couldn't read that file: {error}", "gu": "ફાઇલ વાંચી શકાઈ નહીં: {error}"},

    "scan_method_label": {"en": "Scan method", "gu": "સ્કેન કરવાની રીત"},
    "scan_method_manual": {"en": "⌨️ USB scanner / type", "gu": "⌨️ USB સ્કેનર / ટાઈપ કરો"},
    "scan_method_camera": {"en": "🖼️ Photo from gallery", "gu": "🖼️ ગેલેરીમાંથી ફોટો"},
    "barcode_intro_manual": {"en": "Plug in a USB barcode scanner — it types the code and presses "
                                    "Enter automatically. Click into the box below and scan an item.",
                              "gu": "USB બારકોડ સ્કેનર જોડો — તે કોડ ટાઈપ કરીને આપોઆપ એન્ટર દબાવે છે. "
                                    "નીચેના બોક્સમાં ક્લિક કરી વસ્તુ સ્કેન કરો."},
    "barcode_intro_camera": {"en": "Choose a photo of the barcode from your gallery — it will be "
                                    "read automatically.",
                              "gu": "તમારી ગેલેરીમાંથી બારકોડનો ફોટો પસંદ કરો — તે આપોઆપ વંચાઈ જશે."},
    "camera_capture_label": {"en": "Choose a photo of the barcode", "gu": "બારકોડનો ફોટો પસંદ કરો"},
    "camera_detected": {"en": "Barcode detected: **{code}**", "gu": "બારકોડ મળ્યો: **{code}**"},
    "camera_no_barcode": {"en": "Couldn't find a barcode in that photo — try a clearer, closer, "
                                 "well-lit photo of the barcode.",
                           "gu": "ફોટામાં બારકોડ મળ્યો નથી — વધુ સ્પષ્ટ, નજીકનો અને સારા પ્રકાશવાળો ફોટો પસંદ કરો."},
    "camera_unavailable": {"en": "Photo-based scanning isn't set up on this server yet — the `pyzbar` "
                                  "package and `libzbar0` system library need to be added "
                                  "(see requirements.txt / packages.txt). Use USB scanner / type for now.",
                            "gu": "આ સર્વર પર ફોટો સ્કેનિંગ હજુ સેટ નથી થયું. હાલ પૂરતું USB સ્કેનર / "
                                  "ટાઈપનો ઉપયોગ કરો."},
    "scan_or_type": {"en": "Scan or type barcode", "gu": "બારકોડ સ્કેન કરો અથવા ટાઈપ કરો"},
    "look_up": {"en": "Look up", "gu": "શોધો"},
    "match_found": {"en": "Match found: **{name}** ({category}) — current stock {stock}, ₹{price}",
                     "gu": "મેળ મળ્યો: **{name}** ({category}) — હાલનો સ્ટોક {stock}, ₹{price}"},
    "add_to_stock": {"en": "Add to stock", "gu": "સ્ટોકમાં ઉમેરો"},
    "restock": {"en": "Restock", "gu": "ફરી સ્ટોક કરો"},
    "stock_updated": {"en": "Stock updated — {name} now has {total} units.",
                       "gu": "સ્ટોક અપડેટ થયો — {name} પાસે હવે {total} એકમો છે."},
    "no_product_for_barcode": {"en": "No product found for barcode **{code}**. Add it as a new product:",
                                "gu": "બારકોડ **{code}** માટે કોઈ ઉત્પાદન મળ્યું નથી. નવા ઉત્પાદન તરીકે ઉમેરો:"},
    "create_product": {"en": "Create product", "gu": "ઉત્પાદન બનાવો"},

    "tab_add_by_photo": {"en": "🏷️ Add by photo", "gu": "🏷️ ફોટોથી ઉમેરો"},
    "photo_scan_intro": {"en": "Upload a photo of the product. If the brand or product name is "
                                "visible in the photo, we'll try to match it to an existing product "
                                "automatically — otherwise we'll help you add it as new.",
                          "gu": "ઉત્પાદનનો ફોટો અપલોડ કરો. જો ફોટામાં બ્રાન્ડ અથવા ઉત્પાદનનું નામ દેખાય "
                                "છે, તો અમે તેને હાલના ઉત્પાદન સાથે આપોઆપ મેળવવાનો પ્રયત્ન કરીશું."},
    "photo_scan_upload_label": {"en": "Choose a product photo", "gu": "ઉત્પાદનનો ફોટો પસંદ કરો"},
    "ocr_unavailable": {"en": "Photo recognition isn't set up on this server yet — the `pytesseract` "
                               "package and `tesseract-ocr` system dependency need to be added "
                               "(see requirements.txt / packages.txt). Add products manually for now.",
                         "gu": "આ સર્વર પર ફોટો ઓળખ હજુ સેટ નથી થઈ. હાલ પૂરતું ઉત્પાદન જાતે ઉમેરો."},
    "photo_match_found": {"en": "Recognized: **{name}** ({category}) — current stock {stock}, ₹{price}",
                           "gu": "ઓળખાયું: **{name}** ({category}) — હાલનો સ્ટોક {stock}, ₹{price}"},
    "photo_no_match": {"en": "Couldn't confidently match this to an existing product. Check the "
                              "name below and add it.",
                        "gu": "આને હાલના ઉત્પાદન સાથે વિશ્વાસપૂર્વક મેળવી શકાયું નથી. નીચેનું નામ "
                              "તપાસો અને ઉમેરો."},
    "photo_detected_text": {"en": "Text we could read from the photo: \"{text}\"",
                             "gu": "ફોટામાંથી વાંચી શકાયેલ લખાણ: \"{text}\""},

    "search_products": {"en": "Search products", "gu": "ઉત્પાદનો શોધો"},
    "search_placeholder": {"en": "Search by name…", "gu": "નામ પ્રમાણે શોધો…"},
    "all_categories": {"en": "All categories", "gu": "બધી શ્રેણીઓ"},
    "no_products_add_one": {"en": "No products yet — add one from the tabs above.",
                             "gu": "હજુ કોઈ ઉત્પાદન નથી — ઉપરના ટેબમાંથી ઉમેરો."},
    "all_products_title": {"en": "All products", "gu": "બધા ઉત્પાદનો"},
    "no_search_match": {"en": "No products match your search.", "gu": "શોધ સાથે કોઈ ઉત્પાદન મળતું નથી."},
    "product_count": {"en": "{n} product(s)", "gu": "{n} ઉત્પાદન(ો)"},
    "edit": {"en": "Edit", "gu": "સંપાદિત કરો"},
    "stock": {"en": "Stock", "gu": "સ્ટોક"},
    "photo_url": {"en": "Photo URL", "gu": "ફોટો URL"},
    "save": {"en": "Save", "gu": "સાચવો"},
    "product_updated": {"en": "{name} updated.", "gu": "{name} અપડેટ થયું."},

    # ---- Sales page ----
    "record_a_sale": {"en": "Record a sale", "gu": "વેચાણ નોંધો"},
    "add_products_first": {"en": "Add products first.", "gu": "પહેલા ઉત્પાદનો ઉમેરો."},
    "all_out_of_stock": {"en": "Every product is out of stock — restock before recording sales.",
                          "gu": "બધા ઉત્પાદનો સ્ટોકમાં નથી — વેચાણ નોંધતા પહેલા સ્ટોક ભરો."},
    "product": {"en": "Product", "gu": "ઉત્પાદન"},
    "quantity": {"en": "Quantity", "gu": "જથ્થો"},
    "record_sale": {"en": "Record sale", "gu": "વેચાણ નોંધો"},
    "recent_sales": {"en": "Recent sales", "gu": "તાજેતરના વેચાણ"},
    "no_sales_recorded": {"en": "No sales recorded yet.", "gu": "હજુ કોઈ વેચાણ નોંધાયું નથી."},
    "not_enough_stock": {"en": "Not enough stock to complete this sale.",
                          "gu": "આ વેચાણ પૂરું કરવા માટે પૂરતો સ્ટોક નથી."},
    "sale_recorded": {"en": "Sale recorded — ₹{total}", "gu": "વેચાણ નોંધાયું — ₹{total}"},

    # ---- Reports page ----
    "reports_intro": {"en": "Download a full Excel workbook with your current product catalogue and "
                             "sales history — one sheet each, styled and ready to share.",
                       "gu": "તમારી હાલની ઉત્પાદન યાદી અને વેચાણ ઇતિહાસ સાથે સંપૂર્ણ Excel ફાઇલ ડાઉનલોડ કરો."},
    "nothing_to_export": {"en": "Nothing to export yet.", "gu": "હજુ નિકાસ કરવા માટે કંઈ નથી."},
    "download_excel": {"en": "⬇ Download Excel report", "gu": "⬇ Excel રિપોર્ટ ડાઉનલોડ કરો"},

    # ---- Table column headers ----
    "col_name": {"en": "Name", "gu": "નામ"},
    "col_category": {"en": "Category", "gu": "શ્રેણી"},
    "col_stock": {"en": "Stock", "gu": "સ્ટોક"},
    "col_barcode": {"en": "Barcode", "gu": "બારકોડ"},
    "col_product": {"en": "Product", "gu": "ઉત્પાદન"},
    "col_qty": {"en": "Qty", "gu": "જથ્થો"},
    "col_total": {"en": "Total (₹)", "gu": "કુલ (₹)"},
    "col_date": {"en": "Date", "gu": "તારીખ"},

    # ---- Page subtitles (brand header tag) ----
    "page_dashboard": {"en": "DASHBOARD", "gu": "ડેશબોર્ડ"},
    "page_products": {"en": "PRODUCTS", "gu": "ઉત્પાદનો"},
    "page_sales": {"en": "SALES", "gu": "વેચાણ"},
    "page_reports": {"en": "REPORTS", "gu": "અહેવાલો"},

    "language_label": {"en": "Language", "gu": "ભાષા"},
}


def t(key: str, **kwargs) -> str:
    """Look up a translated string for the current language, falling back to
    English and finally to the raw key if nothing is found. kwargs are used
    to .format() the string when it contains placeholders."""
    lang = st.session_state.get("lang", "en")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    text = entry.get(lang) or entry.get("en") or key
    return text.format(**kwargs) if kwargs else text


def render_lang_toggle(key_suffix: str = ""):
    """A small English / ગુજરાતી switcher. Pass a unique key_suffix if this
    is ever rendered more than once in the same script run."""
    current = st.session_state.get("lang", "en")
    choice = st.radio(
        "Language / ભાષા",
        ["English", "ગુજરાતી"],
        index=0 if current == "en" else 1,
        horizontal=True,
        label_visibility="collapsed",
        key=f"lang_toggle_widget_{key_suffix}",
    )
    new_lang = "en" if choice == "English" else "gu"
    if new_lang != current:
        st.session_state.lang = new_lang
        st.rerun()
