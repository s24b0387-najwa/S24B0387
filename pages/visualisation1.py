import streamlit as st
import pandas as pd
import plotly.express as px

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

BIRTH_URL = "https://dosm.gov.my"

@st.cache_data
def load_data():
    df = pd.read_parquet(BIRTH_URL)
    df["date"] = pd.to_datetime(df["date"])
    
    # Elakkan pengiraan berganda jika dataset mempunyai lajur pecahan
    if "sex" in df.columns:
        df = df[df["sex"] == "both"]
    if "state" in df.columns:
        df = df[df["state"] == "Malaysia"]
        
    return df

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
    "Examine the trends in live births in Malaysia over the years."
)

# ==========================================
# YEAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

min_year = int(df_birth["date"].dt.year.min())
max_year = int(df_birth["date"].dt.year.max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

start_year, end_year = year_range

# ==========================================
# FILTER AND GROUP DATA
# ==========================================

df_filtered = df_birth[
    (df_birth["date"].dt.year >= start_year) &
    (df_birth["date"].dt.year <= end_year)
].copy()

df_annual = (
    df_filtered
    .groupby(df_filtered["date"].dt.year)["abs"]
    .sum()
    .reset_index()
)

df_annual.columns = ["Year", "Total Births"]
df_annual = df_annual.sort_values("Year")

if df_annual.empty:
    st.warning("No data available.")
    st.stop()

# ==========================================
# SUMMARY METRICS
# ==========================================

total_births = df_annual["Total Births"].sum()
average_births = df_annual["Total Births"].mean()
latest_births = df_annual.iloc[-1]["Total Births"]

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
    f"Live Births in {int(df_annual.iloc[-1]['Year'])}",
    f"{latest_births:,.0f}"
)

st.divider()

# ==========================================
# VISUALIZATION 1 - LINE CHART
# ==========================================

st.subheader("Total Annual Live Births in Malaysia")

st.write(
    "This line chart illustrates the changes in the total "
    "number of live births in Malaysia over the selected years. "
    "It helps identify the overall trend and fluctuations "
    "in annual live births."
)

fig = px.line(
    df_annual,
    x="Year",
    y="Total Births",
    markers=True,
    title="Total Annual Live Births in Malaysia",
    labels={
        "Year": "Year",
        "Total Births": "Total Live Births"
    }
)

fig.update_traces(
    line=dict(width=3),
    marker=dict(size=7)
)

fig.update_layout(
    template="plotly_white",
    hovermode="x unified",
    title_x=0.5
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Annual Birth Dataset"):
    st.dataframe(df_annual, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption("Source: Department of Statistics Malaysia (DOSM)")
st.caption("Malaysia Live Birth Analysis | Objective 1")
