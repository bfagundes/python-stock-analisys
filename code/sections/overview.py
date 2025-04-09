"""
Section: Overview
This module renders the overview text for the Stock Analysis Dashboard homepage.
"""

import streamlit as streamlit

def show():
    streamlit.title("Stock Analysis Dashboard")
    streamlit.header("Project Overview")
    streamlit.write("""
        This dashboard allows you to:
        - Analyze Brazilian stocks using Yahoo Finance data
        - Track your personal portfolio
        - Compare stock fundamentals and price performance
        - Explore market benchmarks
    """)