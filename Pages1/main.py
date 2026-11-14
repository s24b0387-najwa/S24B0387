
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Malaysia Data Visualization",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# REGISTER VISUALIZATION PAGES
# ==========================================

objective1 = st.Page(
    "pages/visualisation1.py",
    title="Objective 1 - Live Births",
    icon="📈",
    url_path="objective-1",
    default=True
)

objective2 = st.Page(
    "pages/visualisation2.py",
    title="Objective 2 - Life Expectancy & Income",
    icon="📊",
    url_path="objective-2"
)

# ==========================================
# SIDEBAR NAVIGATION
# ==========================================

pg = st.navigation(
    {
        "Research Objectives": [
            objective1,
            objective2
        ]
    },
    position="sidebar"
)

# ==========================================
# RUN SELECTED PAGE
# ==========================================

pg.run()
