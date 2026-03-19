import pandas as pd
import streamlit as st

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="E-commerce Dashboard", layout="wide")

# -------------------- CUSTOM CSS (DARK MODE SAFE) --------------------
st.markdown("""
<style>

/* Multiselect selected tags */
[data-baseweb="tag"] {
    background-color: #dbeafe !important;
    color: black !important;
    border-radius: 6px;
}

[data-baseweb="tag"]:hover {
    background-color: #bfdbfe !important;
}

/* Ensure text visibility in inputs */
input, .stTextInput input {
    color: inherit !important;
}

/* Dropdown text visibility */
[data-baseweb="select"] {
    color: inherit !important;
}

</style>
""", unsafe_allow_html=True)

# -------------------- LOAD DATA --------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/superstore.csv", encoding='latin1')
    df.columns = df.columns.str.strip()
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    return df

df = load_data()

# -------------------- SIDEBAR --------------------
st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Select Region",
    df["Region"].unique(),
    default=df["Region"].unique()
)

filtered_states = df[df["Region"].isin(region)]["State"].unique()

state = st.sidebar.multiselect(
    "Select State",
    filtered_states,
    default=filtered_states
)

category = st.sidebar.multiselect(
    "Select Category",
    df["Category"].unique(),
    default=df["Category"].unique()
)

start_date = st.sidebar.date_input("Start Date", df["Order Date"].min())
end_date = st.sidebar.date_input("End Date", df["Order Date"].max())

search = st.sidebar.text_input("Search Product")

# -------------------- APPLY FILTERS --------------------
df = df[
    (df["Region"].isin(region)) &
    (df["State"].isin(state)) &
    (df["Category"].isin(category)) &
    (df["Order Date"] >= pd.to_datetime(start_date)) &
    (df["Order Date"] <= pd.to_datetime(end_date))
]

if search:
    df = df[df["Product Name"].str.contains(search, case=False)]

# -------------------- EMPTY CHECK --------------------
if df.empty:
    st.warning("No data available for selected filters")
    st.stop()

# -------------------- TITLE --------------------
st.markdown("<h1 style='text-align: center;'>📊 E-commerce Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# -------------------- KPIs --------------------
st.subheader("Key Metrics")

col1, col2, col3 = st.columns(3)

col1.metric("Total Sales", f"${df['Sales'].sum():,.0f}")
col2.metric("Total Profit", f"${df['Profit'].sum():,.0f}")
col3.metric("Total Quantity", int(df["Quantity"].sum()))

st.markdown("---")

# -------------------- MONTHLY SALES --------------------
st.subheader("Monthly Sales Trend")

df["Month-Year"] = df["Order Date"].dt.to_period("M").astype(str)
monthly_sales = df.groupby("Month-Year")["Sales"].sum().sort_index()

st.line_chart(monthly_sales)

# -------------------- CATEGORY & REGION --------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales by Category")
    st.bar_chart(df.groupby("Category")["Sales"].sum())

with col2:
    st.subheader("Sales by Region")
    st.bar_chart(df.groupby("Region")["Sales"].sum())

st.markdown("---")

# -------------------- STATE ANALYSIS --------------------
st.subheader("Top States by Sales")

top_states = df.groupby("State")["Sales"].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_states)

# -------------------- CITY ANALYSIS --------------------
st.subheader("Top Cities by Sales")

top_cities = df.groupby("City")["Sales"].sum().sort_values(ascending=False).head(10)
top_cities.index = top_cities.index.str[:25]

st.bar_chart(top_cities)

st.markdown("---")

# -------------------- SALES vs PROFIT --------------------
st.subheader("Sales vs Profit")

sales_profit = df.groupby("Category")[["Sales", "Profit"]].sum()
st.line_chart(sales_profit)

# -------------------- SORT OPTION --------------------
sort_option = st.selectbox("Sort Products By", ["Sales", "Profit"])

# -------------------- TOP PRODUCTS --------------------
st.subheader("Top 10 Products")

top_products = df.groupby("Product Name")[sort_option].sum().sort_values(ascending=False).head(10)
top_products.index = top_products.index.str[:30]

st.bar_chart(top_products)

# -------------------- LOSS PRODUCTS --------------------
st.subheader("Top 10 Loss-Making Products")

loss_products = df[df["Profit"] < 0].sort_values(by="Profit")

st.dataframe(
    loss_products[["Product Name", "Category", "Sales", "Profit"]].head(10),
    width='stretch'
)

# -------------------- BEST vs WORST --------------------
st.subheader("Best vs Worst Categories")

top = df.groupby("Category")["Profit"].sum().sort_values(ascending=False).head(3)
bottom = df.groupby("Category")["Profit"].sum().sort_values().head(3)

col1, col2 = st.columns(2)

with col1:
    st.write("Top Categories")
    st.bar_chart(top)

with col2:
    st.write("Worst Categories")
    st.bar_chart(bottom)

# -------------------- INSIGHTS --------------------
st.markdown("---")
st.subheader("📊 Key Insights")

best_category = df.groupby("Category")["Profit"].sum().idxmax()
worst_category = df.groupby("Category")["Profit"].sum().idxmin()
top_region = df.groupby("Region")["Sales"].sum().idxmax()
top_state = df.groupby("State")["Sales"].sum().idxmax()

st.write(f"✅ Most profitable category: **{best_category}**")
st.write(f"⚠️ Least profitable category: **{worst_category}**")
st.write(f"🌍 Top region by sales: **{top_region}**")
st.write(f"🏆 Top state by sales: **{top_state}**")

# -------------------- DATA TABLE --------------------
st.markdown("---")
st.subheader("Filtered Data")

st.dataframe(df, width='stretch')

# -------------------- DOWNLOAD --------------------
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='filtered_data.csv',
    mime='text/csv',
)

# -------------------- ABOUT --------------------
st.markdown("---")
st.subheader("About This Dashboard")

st.write("""
This dashboard analyzes e-commerce sales data to provide insights into sales trends,
profitability, and product performance using interactive filters and visualizations.
""")

# -------------------- FOOTER --------------------
st.markdown("---")
st.caption("Built with Python & Streamlit 🚀")