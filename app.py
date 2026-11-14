
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Malaysia Demographic Dashboard",
    page_icon="📊",
    layout="wide"
)

# ==========================================
# LIGHT THEME
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #F8FAFC;
    }

    h1, h2, h3 {
        color: #1E293B;
    }

    .subtitle {
        color: #64748B;
        font-size: 17px;
    }

    .intro {
        color: #334155;
        font-size: 16px;
        line-height: 1.8;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# MAIN DASHBOARD
# ==========================================

st.title("Malaysia Demographic and Socioeconomic Dashboard")

st.markdown(
    '<p class="subtitle">'
    'An analysis of demographic and socioeconomic trends in Malaysia '
    'using data from the Department of Statistics Malaysia (DOSM).'
    '</p>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# DASHBOARD INTRODUCTION
# ==========================================

st.header("Dashboard Overview")

st.markdown("""
<div class="intro">

This dashboard presents an analysis of Malaysia's demographic
and socioeconomic patterns using datasets from the
Department of Statistics Malaysia (DOSM).

It focuses on three main areas: live birth trends, life
expectancy and income differences, and the relationship
between demographic and socioeconomic indicators.

The visualizations allow users to explore the data, compare
different indicators and identify patterns that help provide
a better understanding of Malaysia's population and
socioeconomic development.

</div>
""", unsafe_allow_html=True)

st.divider()


# ==========================================
# RESEARCH OBJECTIVES
# ==========================================

st.header("Research Objectives")

col1, col2, col3 = st.columns(3)

with col1:

    st.subheader("Objective 1")

    st.write(
        "Analyse trends in live births in Malaysia by state, "
        "gender and ethnic group over the years."
    )

    st.caption("Visualization 1: Line Chart")


with col2:

    st.subheader("Objective 2")

    st.write(
        "Compare life expectancy and annual income across "
        "ethnic groups and genders in Malaysia to identify "
        "existing differences."
    )

    st.caption("Visualization 2: Scatter Plot")


with col3:

    st.subheader("Objective 3")

    st.write(
        "Explore the relationship between live births, "
        "life expectancy and annual income to better "
        "understand Malaysia's demographic and "
        "socioeconomic patterns."
    )

    st.caption("Visualization 3: Correlation Heatmap")


st.divider()


# ==========================================
# DATA SOURCES
# ==========================================

st.header("Data Sources")

st.write(
    "The datasets used in this dashboard are obtained from "
    "the Department of Statistics Malaysia (DOSM)."
)

st.markdown("""
- Live Births Dataset
- Life Expectancy Dataset
- Wages by Ethnicity Dataset
- Life Expectancy by State and Ethnicity Dataset
""")

st.divider()


# ==========================================
# NAVIGATION INSTRUCTION
# ==========================================

st.info(
    "To explore the visualizations, select your preferred "
    "research objective from the Pages section in the "
    "sidebar on the left."
)


# ==========================================
# FOOTER
# ==========================================

st.caption(
    "Malaysia Demographic and Socioeconomic Dashboard | DOSM Data Analysis"
)
