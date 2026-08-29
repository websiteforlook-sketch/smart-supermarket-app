# Session Summary — SmartMart (Smart Supermarket Inventory & Sales Analytics System)

**Group 47 — Dept. of Computer Engineering, R. C. Technical Institute, Ahmedabad**
Guide: Prof. Soniya Dadhania

---

## What was delivered this session

### 1. Finished the TiDB Cloud migration

Walked through the remaining steps from the last session's migration plan:
- Generate the TiDB password (Connect panel, shown once).
- Copy the full prefixed username, host (`gateway01.ap-southeast-1.prod.aws.tidbcloud.com`), and port (`4000`).
- Update Streamlit Cloud → App Settings → Secrets with the new `[mysql]` block.
- Push updated `db.py` / `requirements.txt` to GitHub; `init_tables()` auto-creates schema on first connection.
- Flagged that old Aiven data does **not** carry over automatically — export via `mysqldump` first if it needs to be kept (not done yet, still an open item if that data matters).

### 2. Signup / login flow rework

- **Signup now collects**: Shop Name, Shop Owner Name, Username, Password, Confirm Password (previously just username/password).
- **Login stays simple**: Username + Password.
- **Forgot password** added: username + new password + confirm, with a `db.reset_password()` function. (Note: no email/OTP infrastructure, so this is a direct reset once the username is confirmed to exist — a reasonable trade-off for a student project, not bank-grade security.)
- **Fixed a real UX bug**: originally, creating an account dropped the user back at the login screen. Now `create_user()` is immediately followed by `verify_user()` and the session is populated right away — signup goes straight into the dashboard with a welcome toast.

### 3. A chain of production crashes, debugged one at a time

| Symptom | Root cause | Fix |
|---|---|---|
| Generic "Oh no" Streamlit error page | `app.py` missing from the GitHub repo — likely saved without the `.py` extension when downloaded | Confirmed the repo's main file path/name matched Streamlit Cloud's "Main file path" setting |
| `free(): invalid next size` / `double free or corruption` crashes (C-level, not a Python exception) | `mysql-connector-python`'s compiled C extension isn't yet compatible with the very new Python 3.14 runtime Streamlit Cloud was using | Added `use_pure=True` to `mysql.connector.connect()` in `db.py`, forcing the pure-Python driver path |
| `OperationalError: Lost connection ... SSL RECORD_LAYER_FAILURE` | TiDB Cloud Serverless scales to zero when idle; the first query after a cold start can hit a dropped/broken TLS session mid-wakeup | Added a `_with_retry` decorator in `db.py` that clears the cached connection and retries (with backoff) on any function that previously had **no error handling at all** — `init_tables`, `verify_user`, `user_exists`, `get_products`, `get_product_by_barcode`, `restock_product`, `update_stock`, `get_sales` |

### 4. Aesthetic redesign — twice

**First pass**: refined the existing ink-green/gold "receipt ledger" identity — perforated KPI-card edges, ledger-rule panel texture, fixed sidebar contrast, tightened default Streamlit spacing, polished the auth screen with a two-column hero + card layout.

**Second pass, after a screenshot showed blank white boxes on the dashboard**: found the actual bug — every content panel used a broken pattern (`st.markdown('<div class="panel">')` ... other widgets ... `st.markdown("</div>")` as three *separate* Streamlit calls). Streamlit renders each call as a sibling element, not nested content, so the div wrapped nothing and rendered as an empty box while the real content sat outside it, unstyled.

**The fix**: replaced every instance across `app.py` with real `st.container(key="...")` blocks (a `panel()` helper function), which Streamlit actually treats as a wrapping parent. `styling.py` now targets these via `div[class*="st-key-panel_"]` instead of a plain `.panel` class. This was applied consistently to every panel, the KPI row, and the auth card. Also added proper empty-state styling (centered icon + message) instead of plain muted text floating in a broken box.

---

## Current file state (all three delivered this session)

- **`app.py`** — auto-login after signup; forgot-password flow; all panels rebuilt on `st.container(key=...)`; empty-state helper; sidebar nav with icons.
- **`db.py`** — TiDB-ready connection with `use_pure=True`; `shop_name`/`owner_name` columns (with idempotent `ALTER TABLE` migration for older deployments); `reset_password()`; retry-with-backoff wrapper (`_with_retry`) applied to every previously-unprotected read/write function.
- **`styling.py`** — full CSS rewrite around real container keys; perforated KPI-stub cards; ledger-rule panel texture; fixed sidebar button contrast; pill-style nav with active-state highlight; polished auth hero/card layout.

---

## Open items / next steps

- [ ] Decide whether to migrate old Aiven data (export via `mysqldump`/Workbench before it's lost for good — not done yet).
- [ ] Double-check every downloaded file is saved with its correct extension (`app.py`, `db.py`, `styling.py`) before pushing — this chat's file cards show names without extensions, which caused the "main module does not exist" crash once already.
- [ ] If the C-extension/Python-3.14 crash recurs even with `use_pure=True`, pin an older Python version (3.11 or 3.12) in Streamlit Cloud's app settings — some other compiled dependency (matplotlib, pandas) could hit the same ABI mismatch.
- [ ] Full end-to-end retest on the live app: signup → auto-login → dashboard, barcode restock flow, bulk upload, sales recording, Excel export — now that the panel-container fix and retry logic are both in place.
- [ ] Consider whether "Forgot password" needs stronger verification than username-only if this ever handles real shop data (currently intentionally lightweight for a student project).
