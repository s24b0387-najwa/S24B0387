
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Life Expectancy and Income Analysis",
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
# DATASET URLS
# ==========================================

LIFE_URL = (
    "https://storage.dosm.gov.my/demography/"
    "life_expectancy.parquet"
)

WAGES_URL = (
    "https://storage.dosm.gov.my/labour/"
    "wages_ethnicity.parquet"
)

# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    df_life = pd.read_parquet(LIFE_URL)
    df_wages = pd.read_parquet(WAGES_URL)

    return df_life, df_wages

try:
    df_life, df_wages = load_data()
except Exception as e:
    st.error(f"Unable to load datasets: {e}")
    st.stop()

# ==========================================
# CLEAN DATA
# ==========================================

df_life_clean = df_life[
    (df_life["sex"].isin(["male", "female"])) &
    (~df_life["ethnicity"].isin(["overall", "citizen"]))
].copy()

df_wages_clean = df_wages[
    (df_wages["sex"].isin(["male", "female"])) &
    (~df_wages["ethnicity"].isin(["overall", "citizen"]))
].copy()

# ==========================================
# GROUP DATA
# ==========================================

df_life_grouped = (
    df_life_clean
    .groupby(["ethnicity", "sex"], as_index=False)
    ["life_expectancy"].mean()
)

df_wages_grouped = (
    df_wages_clean
    .groupby(["ethnicity", "sex"], as_index=False)
    ["wages_median"].mean()
)

# ==========================================
# MERGE DATASETS
# ==========================================

df_combined = pd.merge(
    df_life_grouped,
    df_wages_grouped,
    on=["ethnicity", "sex"],
    how="inner"
)

if df_combined.empty:
    st.warning("No matching data found.")
    st.stop()

# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("Life Expectancy and Income Analysis")

st.markdown(
    '<p class="subtitle">'
    'Comparing life expectancy and median monthly wages '
    'among different ethnic groups and genders in Malaysia.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# RESEARCH OBJECTIVE 2
# ==========================================

st.subheader("Research Objective 2")

st.info(
    "Compare life expectancy and income among different "
    "ethnic groups and genders in Malaysia to identify "
    "existing differences and gaps."
)

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.title("Dashboard Filters")

selected_gender = st.sidebar.selectbox(
    "Select Gender",
    ["All Genders", "Male", "Female"]
)

ethnicity_options = sorted(
    df_combined["ethnicity"].unique()
)

selected_ethnicity = st.sidebar.selectbox(
    "Select Ethnic Group",
    ["All Ethnic Groups"] + ethnicity_options
)

# ==========================================
# APPLY FILTERS
# ==========================================

df_display = df_combined.copy()

if selected_gender != "All Genders":
    df_display = df_display[
        df_display["sex"] == selected_gender.lower()
    ]

if selected_ethnicity != "All Ethnic Groups":
    df_display = df_display[
        df_display["ethnicity"] == selected_ethnicity
    ]

if df_display.empty:
    st.warning("No data available for selected filters.")
    st.stop()

# ==========================================
# SUMMARY METRICS
# ==========================================

col1, col2, col3 = st.columns(3)

col1.metric(
    "Ethnic-Gender Groups",
    f"{len(df_display)}"
)

col2.metric(
    "Average Life Expectancy",
    f"{df_display['life_expectancy'].mean():.2f} years"
)

col3.metric(
    "Average Monthly Wage",
    f"RM {df_display['wages_median'].mean():,.2f}"
)

st.divider()

# ==========================================
# VISUALIZATION 2 - SCATTER PLOT
# ==========================================

st.subheader("Life Expectancy vs Median Monthly Wages")

st.write(
    "This scatter plot compares average life expectancy "
    "and median monthly wages among different ethnic groups "
    "and genders in Malaysia. Each point represents an "
    "ethnic group and gender combination."
)

fig = px.scatter(
    df_display,
    x="wages_median",
    y="life_expectancy",
    color="sex",
    symbol="ethnicity",
    hover_name="ethnicity",
    hover_data={
        "sex": True,
        "wages_median": ":,.2f",
        "life_expectancy": ":.2f"
    },
    title="Life Expectancy vs Median Monthly Wages",
    labels={
        "wages_median": "Median Monthly Wage (RM)",
        "life_expectancy": "Life Expectancy (Years)",
        "sex": "Gender",
        "ethnicity": "Ethnic Group"
    }
)

fig.update_traces(
    marker=dict(size=13, opacity=0.8)
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Combined Dataset"):
    st.dataframe(df_display, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption("Data Sources: Department of Statistics Malaysia (DOSM)")
st.caption("Life Expectancy and Income Analysis | Objective 2")
