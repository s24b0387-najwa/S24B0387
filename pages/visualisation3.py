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
# DATASET URLS
# ==========================================

BIRTH_URL = "https://storage.dosm.gov.my/demography/birth.parquet"
WAGES_URL = "https://storage.dosm.gov.my/labour/wages_ethnicity.parquet"
LIFE_URL = "https://dosm.gov.my"

# ==========================================
# LOAD DATA
# ==========================================

@st.cache_data
def load_data():
    df_birth = pd.read_parquet(BIRTH_URL)
    df_wages = pd.read_parquet(WAGES_URL)
    df_life = pd.read_parquet(LIFE_URL)

    for df in [df_birth, df_wages, df_life]:
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])

    return df_birth, df_wages, df_life

try:
    df_birth_raw, df_wages_raw, df_life_raw = load_data()
except Exception as e:
    st.error(f"Unable to load datasets: {e}")
    st.stop()

# ==========================================
# PREPARE BIRTH DATA
# ==========================================

df_b = df_birth_raw.copy()

if "state" in df_b.columns:
    df_b = df_b[df_b["state"] == "Malaysia"]
if "sex" in df_b.columns:
    df_b = df_b[df_b["sex"] == "both"]
if "ethnicity" in df_b.columns:
    df_b = df_b[df_b["ethnicity"] == "overall"]

df_b["year"] = df_b["date"].dt.year

df_b_nat = (
    df_b.groupby("year", as_index=False)
    .agg(
        total_births=("abs", "sum"),
        birth_rate=("rate", "mean")
    )
)

# ==========================================
# PREPARE WAGES DATA
# ==========================================

df_w = df_wages_raw.copy()

df_w = df_w[
    (df_w["sex"] == "both") &
    (df_w["ethnicity"] == "overall")
].copy()

df_w["year"] = df_w["date"].dt.year

df_w_nat = (
    df_w.groupby("year", as_index=False)
    .agg(
        wages_median=("wages_median", "mean"),
        wages_mean=("wages_mean", "mean")
    )
)

# ==========================================
# PREPARE LIFE EXPECTANCY DATA
# ==========================================

df_l = df_life_raw.copy()

if "state" in df_l.columns:
    df_l = df_l[df_l["state"] == "Malaysia"]
if "age" in df_l.columns:
    df_l = df_l[df_l["age"] == 0]

df_l = df_l[
    (df_l["sex"] == "both") &
    (df_l["ethnicity"] == "overall")
].copy()

df_l["year"] = df_l["date"].dt.year

df_l_nat = (
    df_l.groupby("year", as_index=False)["life_expectancy"]
    .mean()
)

# ==========================================
# MERGE ALL DATASETS
# ==========================================

df_demographics = pd.merge(
    df_b_nat,
    df_w_nat,
    on="year",
    how="inner"
)

df_demographics = pd.merge(
    df_demographics,
    df_l_nat[["year", "life_expectancy"]],
    on="year",
    how="inner"
)

df_demographics = df_demographics.sort_values("year")

if df_demographics.empty:
    st.warning("No matching annual data found.")
    st.stop()

# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("Demographic and Socioeconomic Analysis")

st.markdown(
    '<p class="subtitle">'
    'Exploring the relationship between live births, '
    'life expectancy and income in Malaysia.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# RESEARCH OBJECTIVE 3
# ==========================================

st.subheader("Research Objective 3")

st.info(
    "Explore the relationship between live births, "
    "life expectancy, and annual income to better understand "
    "Malaysia's demographic and socioeconomic patterns."
)

# ==========================================
# YEAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

available_years = sorted(df_demographics["year"].unique())

selected_years = st.sidebar.multiselect(
    "Select Years",
    options=available_years,
    default=available_years
)

df_display = df_demographics[
    df_demographics["year"].isin(selected_years)
].copy()

if df_display.empty:
    st.warning("Please select at least one year.")
    st.stop()

# ==========================================
# SUMMARY METRICS
# ==========================================

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Years Analysed",
    f"{len(df_display)}"
)

col2.metric(
    "Average Annual Births",
    f"{df_display['total_births'].mean():,.0f}"
)

col3.metric(
    "Average Life Expectancy",
    f"{df_display['life_expectancy'].mean():.2f} years"
)

col4.metric(
    "Average Median Monthly Wage",
    f"RM {df_display['wages_median'].mean():,.2f}"
)

st.divider()

# ==========================================
# CORRELATION ANALYSIS
# ==========================================

st.subheader("Relationship Between Demographic and Economic Indicators")

st.write(
    "This heatmap illustrates the correlation between "
    "live births, birth rate, life expectancy and wages "
    "in Malaysia. It helps identify positive and negative "
    "relationships between the selected indicators."
)

indicators = df_display[
    [
        "wages_median",
        "wages_mean",
        "total_births",
        "birth_rate",
        "life_expectancy"
    ]
].copy()

indicators = indicators.rename(
    columns={
        "wages_median": "Median Monthly Wage",
        "wages_mean": "Mean Monthly Wage",
        "total_births": "Total Annual Births",
        "birth_rate": "Crude Birth Rate",
        "life_expectancy": "Life Expectancy"
    }
)

# Calculate Pearson Correlation
corr_matrix = indicators.corr(method="pearson")

# ==========================================
# VISUALIZATION 3 - HEATMAP
# ==========================================

st.subheader("Demographic & Economic Indicator Correlation Heatmap")

fig = px.imshow(
    corr_matrix,
    text_auto=".3f",
    aspect="auto",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Demographic & Economic Indicator Correlation Heatmap",
    labels={
        "x": "Indicators",
        "y": "Indicators",
        "color": "Correlation"
    }
)

fig.update_layout(
    template="plotly_white",
    title_x=0.5,
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# ==========================================
# CORRELATION INTERPRETATION
# ==========================================

st.subheader("Understanding the Correlation")

st.write("""
- **Positive correlation (+):** Both indicators tend to increase together.
- **Negative correlation (-):** One indicator tends to decrease when the other increases.
- **Near zero correlation:** Little or no linear relationship between the indicators.
""")

# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Combined Demographic Dataset"):
    st.dataframe(df_display, use_container_width=True)

with st.expander("View Correlation Values"):
    st.dataframe(
        corr_matrix.style.format("{:.3f}"),
        use_container_width=True
    )

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption("Data Sources: Department of Statistics Malaysia (DOSM)")
st.caption("Demographic and Socioeconomic Analysis | Objective 3")
