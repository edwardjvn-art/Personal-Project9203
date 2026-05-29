import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import bcrypt
import requests
from datetime import datetime
import os

st.set_page_config(page_title="Business Dashboard", page_icon="📊", layout="wide")

DATA = os.path.join(os.path.dirname(__file__), "data")

def check_password(username, password):
    try:
        stored_user = st.secrets["credentials"]["username"]
        stored_hash = st.secrets["credentials"]["password_hash"]
        return username == stored_user and bcrypt.checkpw(password.encode(), stored_hash.encode())
    except:
        return False

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("Business Dashboard")
    st.subheader("Sign in")
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Sign in"):
            if check_password(username, password):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect username or password.")
    st.stop()

@st.cache_data(ttl=300)
def load_properties():
    return pd.read_csv(f"{DATA}/properties.csv")

@st.cache_data(ttl=300)
def load_accounts():
    return pd.read_csv(f"{DATA}/accounts.csv")

@st.cache_data(ttl=300)
def load_cashflow():
    df = pd.read_csv(f"{DATA}/cashflow.csv")
    df["month"] = pd.to_datetime(df["month"])
    return df

def load_tasks():
    return pd.read_csv(f"{DATA}/tasks.csv")

def save_tasks(df):
    df.to_csv(f"{DATA}/tasks.csv", index=False)

@st.cache_data(ttl=60)
def fetch_stock(ticker, api_key):
    try:
        r = requests.get(f"https://finnhub.io/api/v1/quote?symbol={ticker}&token={api_key}", timeout=5)
        d = r.json()
        return {"ticker": ticker, "price": d.get("c",0), "pct": d.get("dp",0), "high": d.get("h",0), "low": d.get("l",0)}
    except:
        return {"ticker": ticker, "price": 0, "pct": 0, "high": 0, "low": 0}

props    = load_properties()
accounts = load_accounts()
cashflow = load_cashflow()

occupied      = props[props["rent_status"] != "Vacant"]
total_rent    = occupied["monthly_rent"].sum()
total_mtg_pay = props["mortgage_monthly"].sum()
net_cashflow  = total_rent - total_mtg_pay
total_balance = accounts["balance"].sum()
total_mtg_bal = props["mortgage_balance"].sum()
n_occupied    = len(occupied)
n_total       = len(props)

col1, col2 = st.columns([6,1])
with col1:
    st.title("Business Overview")
    st.caption(datetime.now().strftime("%A, %d %B %Y"))
with col2:
    if st.button("Sign out"):
        st.session_state["authenticated"] = False
        st.rerun()

st.divider()

m1,m2,m3,m4,m5 = st.columns(5)
m1.metric("Properties", f"{n_occupied}/{n_total} occupied")
m2.metric("Monthly Rent", f"£{total_rent:,.0f}")
m3.metric("Mortgage Payments", f"£{total_mtg_pay:,.0f}/mo")
m4.metric("Net Cash Flow", f"£{net_cashflow:,.0f}", delta=f"£{net_cashflow-2300:+,.0f} vs last mo")
m5.metric("Total Mortgage", f"£{total_mtg_bal/1e6:.2f}M")

st.divider()

col_props, col_mtg = st.columns(2)

with col_props:
    st.subheader("Rental Properties")
    for _, r in props.iterrows():
        beds = f"{int(r['bedrooms'])}-bed" if r["bedrooms"] > 0 else "Studio"
        end  = pd.to_datetime(r["tenancy_end"]).strftime("%b %Y") if pd.notna(r["tenancy_end"]) and str(r["tenancy_end"]) != "" else "—"
        rent = f"£{r['monthly_rent']:,.0f}/mo" if pd.notna(r["monthly_rent"]) else "Vacant"
        status = r["rent_status"]
        icon = "✅" if status == "Paid" else "⚠️" if status == "Due" else "🔴" if status == "Overdue" else "⬜"
        with st.container(border=True):
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f"**{r['address']}**")
                st.caption(f"{beds} · Ends {end}")
            with c2:
                st.markdown(f"**{rent}**")
                st.markdown(f"{icon} {status}")

with col_mtg:
    st.subheader("Mortgages")
    with st.container(border=True):
        for _, r in props.iterrows():
            if pd.isna(r["mortgage_lender"]) or str(r["mortgage_lender"]) == "": continue
            flag = "⚠️ Tracker" if r["mortgage_type"] == "Tracker" else "🔒 Fixed"
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f"**{r['mortgage_lender']}** · {flag}")
                st.caption(f"£{r['mortgage_balance']:,.0f} · {r['mortgage_rate']}% · ends {pd.to_datetime(r['mortgage_end']).strftime('%Y')}")
            with c2:
                st.markdown(f"**£{r['mortgage_monthly']:,.0f}/mo**")
            st.divider()

    st.subheader("Bank Balances")
    with st.container(border=True):
        for _, r in accounts.iterrows():
            c1, c2 = st.columns([3,1])
            with c1:
                st.markdown(f"**{r['account_name']}**")
                st.caption(f"{r['bank']} · {r['type']}")
            with c2:
                st.markdown(f"**£{r['balance']:,.2f}**")
        st.divider()
        st.metric("Total", f"£{total_balance:,.2f}")

st.divider()

col_tasks, col_cal, col_stocks = st.columns(3)

with col_tasks:
    st.subheader("To-do Today")
    tasks_df = load_tasks()
    updated = False
    for i, row in tasks_df.iterrows():
        tag = f" `{row['tag']}`" if pd.notna(row["tag"]) and str(row["tag"]) != "" else ""
        checked = st.checkbox(f"{row['task']}{tag}", value=bool(row["done"]), key=f"task_{i}")
        if checked != bool(row["done"]):
            tasks_df.at[i, "done"] = checked
            updated = True
    if updated:
        save_tasks(tasks_df)
        st.rerun()
    st.divider()
    with st.expander("Add task"):
        new_task = st.text_input("Task")
        new_tag  = st.selectbox("Tag", ["","Urgent","Property","Finance","Admin"])
        if st.button("Add") and new_task:
            tasks_df = pd.concat([tasks_df, pd.DataFrame([{"task":new_task,"done":False,"tag":new_tag}])], ignore_index=True)
            save_tasks(tasks_df)
            st.rerun()

with col_cal:
    st.subheader("Upcoming Events")
    events = [
        ("Mon",   "Barclays mortgage review",   "10:00 AM"),
        ("Tue",   "Tenant check-in · Oak Lane", "2:00 PM"),
        ("Wed",   "Accountant — Q1 review",     "11:30 AM"),
        ("Fri",   "Church View viewing",         "3:00 PM"),
        ("2 Jun", "NatWest rate decision",        "All day"),
    ]
    for day, title, time in events:
        with st.container(border=True):
            c1, c2 = st.columns([1,3])
            c1.markdown(f"**{day}**")
            with c2:
                st.markdown(f"**{title}**")
                st.caption(time)

with col_stocks:
    st.subheader("Stock Watchlist")
    try:
        api_key   = st.secrets["stocks"]["finnhub_api_key"]
        watchlist = st.secrets["stocks"]["watchlist"]
        if api_key:
            for ticker in watchlist:
                q = fetch_stock(ticker, api_key)
                up = q["pct"] >= 0
                with st.container(border=True):
                    c1, c2 = st.columns([2,1])
                    c1.markdown(f"**{q['ticker']}**")
                    c1.caption(f"H: {q['high']:.2f} · L: {q['low']:.2f}")
                    c2.markdown(f"**{q['price']:.2f}**")
                    c2.markdown(f"{'🟢' if up else '🔴'} {q['pct']:.2f}%")
        else:
            st.info("Add your Finnhub API key to secrets.toml to see live prices.\n\nFree key at finnhub.io")
    except:
        st.info("Add your Finnhub API key to secrets.toml to see live prices.\n\nFree key at finnhub.io")

st.divider()

col_chart, col_blank = st.columns([1.6, 1])

with col_chart:
    st.subheader("Cash Flow — Last 6 Months")
    fig = go.Figure()
    fig.add_bar(x=cashflow["month"].dt.strftime("%b %Y"), y=cashflow["income"], name="Income", marker_color="#378ADD")
    fig.add_bar(x=cashflow["month"].dt.strftime("%b %Y"), y=cashflow["expenses"], name="Expenses", marker_color="#E0E0E0")
    fig.add_scatter(x=cashflow["month"].dt.strftime("%b %Y"), y=cashflow["net"], name="Net", mode="lines+markers", line=dict(color="#1D9E75", width=2.5))
    fig.update_layout(barmode="group", plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=0,r=0,t=10,b=0), height=300, yaxis=dict(tickprefix="£", gridcolor="#F0F0F0"), legend=dict(orientation="h", y=-0.2))
    st.plotly_chart(fig, use_container_width=True)

with col_blank:
    st.subheader("Reserved Panel")
    st.info("This space is reserved for a future panel — ask your developer to add something here!")

st.divider()
st.subheader("Future Panels")
bp1, bp2, bp3 = st.columns(3)
for col in [bp1, bp2, bp3]:
    with col:
        st.info("Reserved panel — coming soon")

st.caption(f"Last refreshed {datetime.now().strftime('%H:%M:%S')}")
