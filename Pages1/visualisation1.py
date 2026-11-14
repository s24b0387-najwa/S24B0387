import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Malaysia Live Birth Analysis",
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
# DATASET URL
# ==========================================

BIRTH_URL = (
    "https://storage.dosm.gov.my/demography/birth.parquet"
)


# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():

    df_birth = pd.read_parquet(BIRTH_URL)

    df_birth["date"] = pd.to_datetime(
        df_birth["date"]
    )

    return df_birth


try:

    df_birth = load_data()

except Exception as e:

    st.error(f"Unable to load dataset: {e}")
    st.stop()


# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("Malaysia Live Birth Analysis")

st.markdown(
    '<p class="subtitle">'
    'An analysis of live birth trends in Malaysia '
    'from 2000 to 2025.'
    '</p>',
    unsafe_allow_html=True
)

st.markdown("---")


# ==========================================
# RESEARCH OBJECTIVE
# ==========================================

st.subheader("Research Objective 1")

st.info(
    "Examine the trends in live births in Malaysia "
    "over the years based on state, gender, and ethnic group."
)


st.write("")


# ==========================================
# SIDEBAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

st.sidebar.markdown("### Year Range")

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
# KEY METRICS
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

st.subheader("1. Total Annual Live Births")

st.markdown(
    "This visualization shows the changes in the total "
    "number of live births in Malaysia over the selected years."
)

fig1 = px.line(
    df_filtered,
    x="date",
    y="abs",
    markers=True,
    title="Total Annual Live Births in Malaysia",
    labels={
        "date": "Year",
        "abs": "Total Live Births"
    }
)

fig1.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# ==========================================
# VISUALIZATION 2
# CRUDE BIRTH RATE
# ==========================================

st.subheader("2. Crude Birth Rate")

st.markdown(
    "This visualization presents the crude birth rate "
    "per 1,000 population and shows how the birth rate "
    "changes over time."
)

fig2 = px.line(
    df_filtered,
    x="date",
    y="rate",
    markers=True,
    title="Crude Birth Rate per 1,000 Population",
    labels={
        "date": "Year",
        "rate": "Crude Birth Rate (per 1,000)"
    }
)

fig2.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# ==========================================
# VISUALIZATION 3
# ANNUAL NET CHANGE IN LIVE BIRTHS
# ==========================================

st.subheader("3. Annual Net Change in Live Births")

st.markdown(
    "This visualization compares the yearly increase or "
    "decrease in the number of live births in Malaysia."
)

df_yoy = df_filtered.copy()

df_yoy["yoy_change"] = df_yoy["abs"].diff()

df_yoy = df_yoy.dropna(
    subset=["yoy_change"]
)

fig3 = px.bar(
    df_yoy,
    x="date",
    y="yoy_change",
    title="Annual Net Change in Live Births",
    labels={
        "date": "Year",
        "yoy_change": "Net Change in Births"
    },
    color="yoy_change",
    color_continuous_scale="RdBu"
)

fig3.add_hline(
    y=0,
    line_dash="dash"
)

fig3.update_layout(
    template="plotly_white",
    hovermode="x unified"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Dataset"):

    st.dataframe(
        df_filtered,
        use_container_width=True
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "Data Source: Department of Statistics Malaysia (DOSM)"
)

st.caption(
    "Malaysia Live Birth Analysis | 2000–2025"
)
