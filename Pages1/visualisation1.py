import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================


    page_title="Live Birth Trends in Malaysia",
    page_icon="📊",
    layout="wide"


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
        font-size: 16px;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# LOAD DATASET
# ==========================================

BIRTH_URL = (
    "https://storage.dosm.gov.my/demography/birth.parquet"
)

@st.cache_data
def load_data():

    df = pd.read_parquet(BIRTH_URL)

    df["date"] = pd.to_datetime(df["date"])

    return df


try:
    df_birth = load_data()

except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()


# ==========================================
# DASHBOARD TITLE
# ==========================================

st.title("Malaysia Live Birth Analysis")

st.markdown(
    '<p class="subtitle">'
    'Exploring live birth trends in Malaysia from 2000 to 2025.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()


# ==========================================
# RESEARCH OBJECTIVE 1
# ==========================================

st.subheader("Research Objective 1")

st.info(
    "Examine the trends in live births in Malaysia over the years"
)

st.write("")


# ==========================================
# YEAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=2000,
    max_value=2025,
    value=(2000, 2025),
    step=1
)

start_year, end_year = year_range


# ==========================================
# FILTER DATA
# ==========================================

df_filtered = df_birth[
    (df_birth["date"].dt.year >= start_year) &
    (df_birth["date"].dt.year <= end_year)
].copy()

df_filtered = df_filtered.sort_values("date")


# ==========================================
# SUMMARY METRICS
# ==========================================

total_births = df_filtered["abs"].sum()

average_births = (
    df_filtered["abs"].mean()
    if not df_filtered.empty else 0
)

latest_births = (
    df_filtered.iloc[-1]["abs"]
    if not df_filtered.empty else 0
)

col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Live Births",
    f"{total_births:,.0f}"
)

col2.metric(
    "Average Annual Births",
    f"{average_births:,.0f}"
)

col3.metric(
    f"Live Births in {end_year}",
    f"{latest_births:,.0f}"
)


st.divider()


# ==========================================
# VISUALIZATION 1
# TOTAL ANNUAL LIVE BIRTHS
# ==========================================

st.subheader("Total Annual Live Births in Malaysia")

st.write(
    "This line chart illustrates the changes in the total "
    "number of live births in Malaysia over the selected years. "
    "It helps identify the overall trend and fluctuations "
    "in annual live births."
)

fig = px.line(
    df_filtered,
    x="date",
    y="abs",
    markers=True,
    title="Total Annual Live Births in Malaysia (2000–2025)",
    labels={
        "date": "Year",
        "abs": "Total Live Births"
    }
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=7)
)

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    xaxis_title="Year",
    yaxis_title="Total Live Births",
    title_x=0.5
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Source: Department of Statistics Malaysia (DOSM)"
)

st.caption(
    "Malaysia Live Birth Analysis | Objective 1"
)
