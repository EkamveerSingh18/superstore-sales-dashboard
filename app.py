
import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Superstore Sales Dashboard")
st.caption("E-Commerce Sales Analysis using MongoDB and PyMongo")

# Connect to MongoDB Atlas using Streamlit Secrets
try:
    mongo_uri = st.secrets["MONGO_URI"]
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=10000)
    client.admin.command("ping")

    db = client["superstore_db"]
    orders = db["orders"]

    records = list(orders.find({}, {"_id": 0}))
    df = pd.DataFrame(records)

except Exception as e:
    st.error("MongoDB connection failed. Please check your connection settings.")
    st.stop()

if df.empty:
    st.warning("No records found in MongoDB.")
    st.stop()

# Convert numeric columns
for col in ["Sales", "Profit", "Quantity", "Discount"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(subset=["Sales", "Profit"])

# Sidebar filters
st.sidebar.header("Filters")

categories = st.sidebar.multiselect(
    "Select Category",
    df["Category"].dropna().unique(),
    default=list(df["Category"].dropna().unique())
)

regions = st.sidebar.multiselect(
    "Select Region",
    df["Region"].dropna().unique(),
    default=list(df["Region"].dropna().unique())
)

filtered_df = df[
    df["Category"].isin(categories) &
    df["Region"].isin(regions)
]

# Key Performance Indicators
st.subheader("Business Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Sales", f"${filtered_df['Sales'].sum():,.2f}")
c2.metric("Total Profit", f"${filtered_df['Profit'].sum():,.2f}")
c3.metric("Total Orders", f"{filtered_df['Order ID'].nunique():,}")
c4.metric("Total Quantity", f"{filtered_df['Quantity'].sum():,.0f}")

# Category-wise Sales
st.subheader("Category-wise Sales")
category_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
fig1 = px.bar(category_sales, x="Category", y="Sales",
              color="Category", title="Sales by Category")
st.plotly_chart(fig1, use_container_width=True)

# Region-wise Sales
st.subheader("Region-wise Sales")
region_sales = filtered_df.groupby("Region")["Sales"].sum().reset_index()
fig2 = px.bar(region_sales, x="Region", y="Sales",
              color="Region", title="Sales by Region")
st.plotly_chart(fig2, use_container_width=True)

# Top 5 Profitable Products
st.subheader("Top 5 Profitable Products")
top_products = (
    filtered_df.groupby("Product Name")["Profit"]
    .sum().nlargest(5).reset_index()
)
fig3 = px.bar(top_products, x="Profit", y="Product Name",
              orientation="h", title="Top 5 Profitable Products")
st.plotly_chart(fig3, use_container_width=True)

# Discount vs Profit
st.subheader("Discount vs Profit")
fig4 = px.scatter(filtered_df, x="Discount", y="Profit",
                  title="Relationship between Discount and Profit")
st.plotly_chart(fig4, use_container_width=True)

# Dataset table
st.subheader("Filtered Order Data")
st.dataframe(filtered_df, use_container_width=True)

# Download filtered data
csv = filtered_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Filtered Data",
    data=csv,
    file_name="superstore_filtered_data.csv",
    mime="text/csv"
)
