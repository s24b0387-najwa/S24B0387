import streamlit as st

st.set_page_config(
    page_title="Malaysia Socioeconomic Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("Malaysia Demographic and Socioeconomic Dashboard")

st.write("""
This dashboard presents an analysis of Malaysia's demographic
and socioeconomic trends using data from the Department of
Statistics Malaysia (DOSM).

Use the navigation menu on the left to explore the three
visualisations.
""")

st.info("Please select a visualisation from the sidebar to get started.")
