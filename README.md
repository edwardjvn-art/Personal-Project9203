# Business Dashboard

A personal Streamlit dashboard for tracking rental properties, mortgages,
bank balances, stocks, tasks, and cash flow.

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your password
```bash
python hash_password.py
```
Copy the hash it outputs.

### 3. Configure secrets
Copy the template and fill it in:
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
```
Edit `.streamlit/secrets.toml`:
- Paste your password hash
- Add your Finnhub API key (free at https://finnhub.io)
- Set your stock watchlist tickers

### 4. Fill in your data
Edit the CSV files in the `data/` folder:
- `data/properties.csv` — your rental properties
- `data/accounts.csv`   — your bank accounts
- `data/cashflow.csv`   — monthly income/expense figures
- `data/tasks.csv`      — starting tasks (more can be added in the app)

### 5. Run the app
```bash
streamlit run app.py
```
Open http://localhost:8501 in your browser.

---

## Hosting (so your friend can access it online)

**Easiest — Streamlit Community Cloud (free):**
1. Push the project to a private GitHub repo
2. Go to https://share.streamlit.io
3. Connect your repo and deploy
4. Add your secrets in the Streamlit Cloud dashboard (Settings → Secrets)

**Alternative — run on a VPS (DigitalOcean, Hetzner):**
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
Then point a domain at it with Nginx + SSL.

---

## Data files format

### properties.csv columns
| Column | Example |
|---|---|
| property | 14 Maple Street Bristol |
| address | 14 Maple Street Bristol |
| bedrooms | 2 |
| tenant_name | John Smith |
| monthly_rent | 1400 |
| rent_status | Paid / Due / Overdue / Vacant |
| tenancy_end | 2025-12-01 |
| mortgage_lender | Barclays |
| mortgage_balance | 180000 |
| mortgage_rate | 3.5 |
| mortgage_monthly | 820 |
| mortgage_type | Fixed / Tracker |
| mortgage_end | 2031-01-01 |

### accounts.csv columns
account_name, bank, balance, type

### cashflow.csv columns
month (YYYY-MM), income, expenses, net

---

## Adding new panels

The dashboard has 4 reserved blank panel slots at the bottom.
Each one is a placeholder `st.markdown` block in `app.py` — 
replace it with any Streamlit component you want.
