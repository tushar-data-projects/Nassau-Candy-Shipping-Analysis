
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Nassau Candy Shipping Analysis",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Nassau Candy Distributor")
st.subheader("Factory-to-Customer Shipping Route Efficiency Analysis")

st.markdown("""
This dashboard analyzes shipment records, sales, profit, shipping modes,
and shipping duration to understand logistics performance.
""")

# Load the Excel workbook
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

uploaded_file = st.sidebar.file_uploader(
    "Upload the project Excel workbook",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = load_data(uploaded_file)
else:
    st.info(
        "Please upload the Excel workbook "
        "'project 1 unified.xlsx' using the sidebar."
    )
    st.stop()

# Clean column names
df.columns = df.columns.str.strip()

# Convert date columns
date_columns = ["Order Date", "Ship Date"]

for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Calculate shipping days
if "Order Date" in df.columns and "Ship Date" in df.columns:
    df["Shipping Days"] = (
        df["Ship Date"] - df["Order Date"]
    ).dt.days

# Sidebar filters
st.sidebar.header("Dashboard Filters")

if "Region" in df.columns:
    regions = sorted(df["Region"].dropna().unique())
    selected_regions = st.sidebar.multiselect(
        "Select Region",
        regions,
        default=regions
    )
    df = df[df["Region"].isin(selected_regions)]

if "Ship Mode" in df.columns:
    modes = sorted(df["Ship Mode"].dropna().unique())
    selected_modes = st.sidebar.multiselect(
        "Select Shipping Mode",
        modes,
        default=modes
    )
    df = df[df["Ship Mode"].isin(selected_modes)]

# KPI calculations
total_records = len(df)

total_units = (
    df["Units"].sum()
    if "Units" in df.columns else 0
)

total_sales = (
    df["Sales"].sum()
    if "Sales" in df.columns else 0
)

total_profit = (
    df["Gross Profit"].sum()
    if "Gross Profit" in df.columns else 0
)

average_shipping_days = (
    df["Shipping Days"].mean()
    if "Shipping Days" in df.columns else 0
)

# KPI display
st.header("Key Performance Indicators")

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Shipment Records", f"{total_records:,}")
k2.metric("Total Units", f"{total_units:,.0f}")
k3.metric("Total Sales", f"${total_sales:,.2f}")
k4.metric("Gross Profit", f"${total_profit:,.2f}")
k5.metric(
    "Avg. Shipping Days",
    f"{average_shipping_days:,.2f}"
)

st.divider()

# Regional analysis
st.header("Regional Performance")

if "Region" in df.columns:
    regional_summary = df.groupby("Region", as_index=False).agg(
        Sales=("Sales", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Shipment_Records=("Region", "count")
    )

    col1, col2 = st.columns(2)

    with col1:
        fig_sales = px.bar(
            regional_summary,
            x="Region",
            y="Sales",
            title="Sales by Region",
            text_auto=".2s"
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        fig_profit = px.bar(
            regional_summary,
            x="Region",
            y="Gross_Profit",
            title="Gross Profit by Region",
            text_auto=".2s"
        )
        st.plotly_chart(fig_profit, use_container_width=True)

    st.dataframe(
        regional_summary,
        use_container_width=True
    )

# Shipping mode analysis
st.header("Shipping Mode Analysis")

if "Ship Mode" in df.columns:
    mode_summary = df.groupby("Ship Mode", as_index=False).agg(
        Shipment_Records=("Ship Mode", "count")
    )

    fig_mode = px.bar(
        mode_summary,
        x="Ship Mode",
        y="Shipment_Records",
        title="Shipment Records by Shipping Mode",
        text_auto=True
    )

    st.plotly_chart(
        fig_mode,
        use_container_width=True
    )

# Shipping duration analysis
st.header("Shipping Duration Analysis")

if "Shipping Days" in df.columns:
    valid_shipping_days = df[
        df["Shipping Days"].notna()
    ]

    fig_days = px.histogram(
        valid_shipping_days,
        x="Shipping Days",
        nbins=30,
        title="Distribution of Shipping Days"
    )

    st.plotly_chart(
        fig_days,
        use_container_width=True
    )

    st.metric(
        "Maximum Shipping Days",
        f"{valid_shipping_days['Shipping Days'].max():,.0f}"
    )

# Data quality warning
st.header("Data Quality Observation")

if "Shipping Days" in df.columns:
    if df["Shipping Days"].mean() > 365:
        st.warning("""
        The average shipping duration is unusually high.
        Please verify the Order Date and Ship Date values in the
        source workbook before drawing final conclusions.
        """)

# Detailed records
st.header("Shipment Data")

st.dataframe(
    df,
    use_container_width=True,
    height=400
)

st.caption(
    "Nassau Candy Distributor | Shipping Route Efficiency Analysis"
)
