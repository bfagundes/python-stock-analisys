"""
Main entry point for the Stock Analysis Dashboard.
This Streamlit app provides multiple tools to analyze Brazilian stocks, track a portfolio, and compare market data.
Each section is modularized under the `sections/` folder for better maintainability.
"""

import streamlit as streamlit
from sections import (
    overview, 
    stock_info, 
    stock_comparison,
    portfolio
)

# Page configuration
streamlit.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide"
)

# Sidebar navigation
streamlit.sidebar.title("📊 Stock Analysis")
streamlit.sidebar.markdown("Welcome! Use the menu below to explore.")

# Navigation menu
menu = streamlit.sidebar.selectbox("Choose a section", [
    "Overview",
    "Stock Info",
    "Stock Comparison",
    "Portfolio Tracker"
])

# Route to the appropriate section
if menu == "Overview":
    overview.show()

elif menu == "Stock Info":    
    stock_info.show()

elif menu == "Stock Comparison":
    stock_comparison.show()

elif menu == "Portfolio Tracker":
    portfolio.show()