import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# LIGHT THEME (MATCHING MAIN.PY)
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
# LOAD DATASETS
# ==========================================

URL_BIRTH = "https://storage.dosm.gov.my/demography/birth.parquet"
URL_WAGES = "https://storage.dosm.gov.my/labour/wages_ethnicity.parquet"
URL_LIFE = "https://storage.dosm.gov.my/demography/life_expectancy_state_ethnic.parquet"

@st.cache_data
def load_merged_data():
    df_birth_raw = pd.read_parquet(URL_BIRTH)
    df_birth_raw["date"] = pd.to_datetime(df_birth_raw["date"])

    df_wages_raw = pd.read_parquet(URL_WAGES)
    df_wages_raw["date"] = pd.to_datetime(df_wages_raw["date"])

    df_life_raw = pd.read_parquet(URL_LIFE)
    df_life_raw["date"] = pd.to_datetime(df_life_raw["date"])

    # Filter to national-level, overall demographics
    df_w_nat = df_wages_raw[
        (df_wages_raw["sex"] == "both") &
        (df_wages_raw["ethnicity"] == "overall")
    ][["date", "wages_median", "wages_mean"]]

    df_b_nat = df_birth_raw[["date", "abs", "rate"]].rename(
        columns={"abs": "total_births", "rate": "birth_rate"}
    )

    df_l_nat = df_life_raw[
        (df_life_raw["sex"] == "both") &
        (df_life_raw["ethnicity"] == "overall")
    ].groupby("date", as_index=False)["life_expectancy"].mean()

    # Merge datasets on date
    df_merged = pd.merge(df_w_nat, df_b_nat, on="date", how="inner")
    df_merged = pd.merge(df_merged, df_l_nat, on="date", how="inner")
    df_merged["Year"] = df_merged["date"].dt.year
    return df_merged.sort_values("Year")

try:
    df_demographics = load_merged_data()
except Exception as e:
    st.error(f"Unable to load datasets: {e}")
    st.stop()

# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("Demographic & Economic Correlation Analysis")

st.markdown(
    '<p class="subtitle">'
    'Analyzing statistical relationships between wages, birth rates, and life expectancy in Malaysia.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# RESEARCH OBJECTIVE 3
# ==========================================

st.subheader("Research Objective 3")

st.info(
    "Analyze the correlation between national economic indicators (monthly wages) "
    "and key demographic metrics (live births, crude birth rate, and life expectancy) in Malaysia."
)

# ==========================================
# SIDEBAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

min_year = int(df_demographics["Year"].min())
max_year = int(df_demographics["Year"].max())

year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

df_filtered = df_demographics[
    (df_demographics["Year"] >= year_range[0]) &
    (df_demographics["Year"] <= year_range[1])
].copy()

if len(df_filtered) < 2:
    st.warning("Please select a range of at least 2 years to compute correlations.")
    st.stop()

# ==========================================
# CORRELATION CALCULATION & SUMMARY METRICS
# ==========================================

indicators = df_filtered[
    ["wages_median", "wages_mean", "total_births", "birth_rate", "life_expectancy"]
].rename(columns={
    "wages_median": "Median Monthly Wage",
    "wages_mean": "Mean Monthly Wage",
    "total_births": "Total Annual Births",
    "birth_rate": "Crude Birth Rate",
    "life_expectancy": "Life Expectancy"
})

corr_matrix = indicators.corr()

r_wage_birth = corr_matrix.loc["Median Monthly Wage", "Crude Birth Rate"]
r_wage_life = corr_matrix.loc["Median Monthly Wage", "Life Expectancy"]
overlapping_years = len(df_filtered)

col1, col2, col3 = st.columns(3)

col1.metric("Wage vs. Birth Rate (r)", f"{r_wage_birth:.3f}")
col2.metric("Wage vs. Life Expectancy (r)", f"{r_wage_life:.3f}")
col3.metric("Years Analyzed", f"{overlapping_years} Years")

st.divider()

# ==========================================
# VISUALIZATION 3 - CORRELATION HEATMAP
# ==========================================

st.subheader("Demographic & Economic Indicator Correlation Heatmap")

st.write(
    "This heatmap displays the Pearson correlation coefficients (r) across national wage and demographic indicators. "
    "Values near +1 indicate a strong positive relationship, whereas values near -1 indicate a strong negative relationship."
)

fig = px.imshow(
    corr_matrix,
    text_auto=".3f",
    aspect="auto",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    title="Demographic & Economic Indicator Correlation Heatmap"
)

fig.update_layout(template="plotly_white", height=550, title_x=0.5)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================
# INTERPRETATION / DISCUSSION
# ==========================================

st.subheader("Interpretation & Discussion")

st.markdown("""
* **Inverse Relationship Between Income and Fertility:** The correlation heatmap reveals a strong negative correlation between monthly wages and both total annual births and crude birth rates. As household income increases, fertility rates systematically decline.
* **Positive Association with Longevity:** Median and mean monthly wages exhibit a positive relationship with life expectancy, reflecting how higher living standards and better healthcare access support longer lifespans.
* **Scientific Meaning (Demographic Transition Theory):** These empirical relationships align with the **Demographic Transition Model**, wherein economic modernization, rising wages, and higher opportunity costs of child-rearing drive a shift toward lower birth rates and higher life expectancy.
""")

# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Merged Demographic & Economic Dataset"):
    st.dataframe(df_filtered, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("Source: Department of Statistics Malaysia (DOSM)")
st.caption("Demographic & Economic Correlation Analysis | Objective 3")
