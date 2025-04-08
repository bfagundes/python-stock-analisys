import streamlit as streamlit
from sections import (
    overview, 
    stock_info, 
    stock_comparison
)

# Set page config
streamlit.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Sidebar
streamlit.sidebar.title("📊 Stock Analysis")
streamlit.sidebar.markdown("Welcome! Use the menu below to explore.")

# Sidebar options
menu = streamlit.sidebar.selectbox("Choose a section", [
    "Overview",
    "Stock Info",
    "Stock Comparison"
])

# Main Title
streamlit.title("📈 Stock Analysis Dashboard")

# Show different sections
if menu == "Overview":
    overview.show()

elif menu == "Stock Info":    
    stock_info.show()

elif menu == "Stock Comparison":
    stock_comparison.show()