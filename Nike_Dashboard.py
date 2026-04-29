import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------
# PAGE CONFIG
# ---------------------------
st.set_page_config(page_title="Nike Dashboard", layout="wide")

# ---------------------------
# THEME
# ---------------------------
st.markdown("""
<style>
.stApp {
    background-color: #0e1117;
    color: #e6e6e6;
    font-family: 'Segoe UI', sans-serif;
}
h1 {text-align:center; color:white;}
h3 {color:#f97316;}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #111827, #1f2937);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] {
    background: #111827;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------
# LOAD DATA
# ---------------------------
data = pd.read_excel("D:\\Ujjawal's Data\\Power BI Desktop\\Nike Analysis\\Cleaned_output_final.xlsx")
data["Order_Date"] = pd.to_datetime(data["Order_Date"])

# ---------------------------
# TITLE
# ---------------------------
st.title("👟 Nike Sales Dashboard")
st.markdown("<p style='text-align:center; color:#9ca3af;'>Interactive Sales Analytics Dashboard</p>", unsafe_allow_html=True)

# ---------------------------
# RESET STATE DEFAULTS
# ---------------------------
default_filters = {
    "gender": "All",
    "line": "All",
    "product": "All",
    "status": "All"
}

for key, val in default_filters.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------
# SIDEBAR FILTERS
# ---------------------------
st.sidebar.header("🔎 Filters")

if st.sidebar.button("Reset Filters"):
    for key, val in default_filters.items():
        st.session_state[key] = val
    st.rerun()

gender_filter = st.sidebar.selectbox(
    "Gender",
    ["All"] + list(data["Gender_Category"].dropna().unique()),
    key="gender"
)

product_line_filter = st.sidebar.selectbox(
    "Product Line",
    ["All"] + list(data["Product_Line"].dropna().unique()),
    key="line"
)

product_filter = st.sidebar.selectbox(
    "Product",
    ["All"] + list(data["Product_Name"].dropna().unique()),
    key="product"
)

status_filter = st.sidebar.selectbox(
    "Status",
    ["All"] + list(data["Product_Status"].dropna().unique()),
    key="status"
)

# ---------------------------
# APPLY FILTERS
# ---------------------------
filtered = data.copy()

if gender_filter != "All":
    filtered = filtered[filtered["Gender_Category"] == gender_filter]

if product_line_filter != "All":
    filtered = filtered[filtered["Product_Line"] == product_line_filter]

if product_filter != "All":
    filtered = filtered[filtered["Product_Name"] == product_filter]

if status_filter != "All":
    filtered = filtered[filtered["Product_Status"] == status_filter]

if filtered.empty:
    st.warning("No data available for selected filters")
    st.stop()

# ---------------------------
# KPI CALCULATION
# ---------------------------
total_revenue = filtered['Revenue'].sum()
total_profit = filtered['Profit'].sum()
total_units_sold = filtered['Units_Sold'].sum()
total_orders = filtered['Order_ID'].nunique()

aov = total_revenue / total_orders if total_orders else 0
profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

returned_orders = filtered[filtered['Product_Status'] == 'Returned'].shape[0]
return_rate = (returned_orders / len(filtered)) * 100 if len(filtered) else 0

# ---------------------------
# KPI DISPLAY
# ---------------------------
st.markdown("## 📊 Key Metrics")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders", f"{total_orders:,}")
k2.metric("Revenue", f"${total_revenue/1_000_000:.2f}M")
k3.metric("Profit", f"${total_profit/1_000_000:.2f}M")
k4.metric("Units Sold", f"{total_units_sold:,}")

k5, k6, k7, k8 = st.columns(4)
k5.metric("AOV", f"${aov:,.0f}")
k6.metric("Profit Margin", f"{profit_margin:.1f}%")
k7.metric("Returns", f"{returned_orders:,}")
k8.metric("Return Rate", f"{return_rate:.1f}%")

st.markdown("---")

# ---------------------------
# SALES INSIGHTS
# ---------------------------
st.subheader("📈 Sales Insights")

# Professional color palette
primary = "#3b82f6"
secondary = "#10b981"
accent = "#f97316"

top_selling_product = (
    filtered.groupby('Product_Name')['Units_Sold']
    .sum().sort_values(ascending=True).tail(5).reset_index()
)

top_revenue_product = (
    filtered.groupby('Product_Name')['Revenue']
    .sum().sort_values(ascending=True).tail(5).reset_index()
)

revenue_by_gender = (
    filtered.groupby('Gender_Category')['Revenue']
    .sum().reset_index()
)

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("### 🏆 Top Selling Products")
    st.caption("Products with highest units sold")

    fig = px.bar(
        top_selling_product,
        x="Units_Sold",
        y="Product_Name",
        orientation="h",
        text="Units_Sold"
    )
    fig.update_traces(marker_color=primary)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.markdown("### 💰 Top Revenue Products")
    st.caption("Products generating highest revenue")

    fig = px.bar(
        top_revenue_product,
        x="Revenue",
        y="Product_Name",
        orientation="h",
        text_auto=".2s"
    )
    fig.update_traces(marker_color=secondary)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c3:
    st.markdown("### 👥 Revenue by Gender")
    st.caption("Distribution of revenue across categories")

    fig = px.pie(
        revenue_by_gender,
        names="Gender_Category",
        values="Revenue",
        hole=0.6
    )
    fig.update_traces(marker=dict(colors=[primary, secondary, accent]))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# REGION + CHANNEL
# ---------------------------
st.markdown("---")

c4, c5 = st.columns(2)

with c4:
    st.markdown("### 🌍 Revenue by Region")
    st.caption("Region-wise revenue performance")

    revenue_by_region = filtered.groupby('Region')['Revenue'].sum().reset_index()
    fig = px.bar(revenue_by_region, x="Region", y="Revenue", text_auto=".2s")
    fig.update_traces(marker_color=primary)
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c5:
    st.markdown("### 🛒 Sales Channel Split")
    st.caption("Revenue contribution by channel")

    revenue_by_channel = filtered.groupby('Sales_Channel')['Revenue'].sum().reset_index()
    fig = px.pie(revenue_by_channel, names="Sales_Channel", values="Revenue", hole=0.6)
    fig.update_traces(marker=dict(colors=[secondary, accent]))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# SIZE + TREND
# ---------------------------
st.markdown("---")

c6, c7 = st.columns(2)

with c6:
    st.markdown("### 📏 Size Distribution")
    st.caption("Units sold across size categories")

    stacked_data = (
        filtered.groupby(['Size_Category', 'Size'])['Units_Sold']
        .sum().reset_index()
    )

    fig = px.bar(stacked_data, x="Size_Category", y="Units_Sold",
                 color="Size", barmode="stack")
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with c7:
    st.markdown("### 📅 Monthly Trend")
    st.caption("Revenue and profit over time")

    month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    filtered["Month"] = pd.Categorical(filtered["Month"], categories=month_order, ordered=True)

    monthly_trend = (
        filtered.groupby('Month', observed=False)[['Revenue', 'Profit']]
        .sum().reset_index()
    )

    fig = px.line(monthly_trend, x="Month", y=["Revenue", "Profit"], markers=True)
    fig.update_traces(line=dict(width=3))
    fig.update_layout(template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TABLE
# ---------------------------
st.markdown("---")
st.subheader("📋 Detailed Order Analysis")

grid_data = filtered.sort_values(by="Order_Date", ascending=False)

st.dataframe(grid_data, use_container_width=True, height=500, hide_index=True)