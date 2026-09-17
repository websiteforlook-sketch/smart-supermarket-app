# SmartMart updated files

Replace these files in your Streamlit/GitHub project:
- app.py
- db.py
- i18n.py
- styling.py
- requirements.txt

## Included changes
- New supermarket-focused landing hero instead of “Run your shop, like clockwork.”
- **Create / Log in account** button with smooth scroll to the login section.
- Dashboard KPI cards for **Profit today** and **Loss today**, alongside Products, Stock Value, Sales Today and Low Stock Alerts.
- Product **Cost price** field and CSV/Excel support for `cost_price`.
- Each new sale saves the cost price used at that time, allowing gross profit/loss calculation.
- New **My Profile** sidebar page with shop name, owner name, mobile, email and profile photo upload.
- Automatic additive database migrations for existing TiDB tables.
- English/Gujarati translations for the new UI.

## Important profit/loss note
The old version did not store cost prices for products or historical sales. Existing old sales therefore do not have reliable historical cost data. The dashboard calculates profit/loss from sales that have a saved cost price. Set cost prices for products before recording new sales.

## Run
```bash
streamlit run app.py
```
