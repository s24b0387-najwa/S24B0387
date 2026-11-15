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
# LOAD DATASET
# ==========================================

WAGES_URL = "https://storage.dosm.gov.my/labour/wages_ethnicity.parquet"

@st.cache_data
def load_wages_data():
    df = pd.read_parquet(WAGES_URL)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df

try:
    df_wages = load_wages_data()
except Exception as e:
    st.error(f"Unable to load dataset: {e}")
    st.stop()

# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("Malaysia Median Monthly Wages Analysis")

st.markdown(
    '<p class="subtitle">'
    'Comparing median monthly wages across ethnic groups and genders in Malaysia.'
    '</p>',
    unsafe_allow_html=True
)

st.divider()

# ==========================================
# RESEARCH OBJECTIVE 2
# ==========================================

st.subheader("Research Objective 2")

st.info(
    "Compare the median monthly wages across different ethnic groups and genders in Malaysia."
)

# ==========================================
# SIDEBAR FILTER
# ==========================================

st.sidebar.title("Dashboard Filters")

df_wages_clean = df_wages[
    (df_wages["sex"].isin(["male", "female"])) &
    (~df_wages["ethnicity"].isin(["overall", "citizen"]))
].copy()

df_wages_clean["Year"] = df_wages_clean["date"].dt.year
years = sorted(df_wages_clean["Year"].unique(), reverse=True)

selected_year = st.sidebar.selectbox(
    "Select Time Period",
    options=["All Years (Overall Average)"] + [str(y) for y in years]
)

if selected_year != "All Years (Overall Average)":
    df_filtered = df_wages_clean[df_wages_clean["Year"] == int(selected_year)].copy()
else:
    df_filtered = df_wages_clean.copy()

if df_filtered.empty:
    st.warning("No data available.")
    st.stop()

# ==========================================
# SUMMARY METRICS (SUMMARY BOX)
# ==========================================

overall_median = df_filtered["wages_median"].mean()
male_median = df_filtered[df_filtered["sex"] == "male"]["wages_median"].mean()
female_median = df_filtered[df_filtered["sex"] == "female"]["wages_median"].mean()

col1, col2, col3 = st.columns(3)

col1.metric("Overall Median Wage", f"RM {overall_median:,.2f}")
col2.metric("Male Median Wage", f"RM {male_median:,.2f}")
col3.metric("Female Median Wage", f"RM {female_median:,.2f}")

st.divider()

# ==========================================
# VISUALIZATION 2 - GROUPED BAR CHART
# ==========================================

st.subheader("Median Monthly Wages (RM) by Ethnic Group & Gender")

st.write(
    "This grouped bar chart compares the average median monthly wages between male and female "
    "workers across major ethnic groups in Malaysia for the selected time period."
)

df_wages_grouped = (
    df_filtered
    .groupby(["ethnicity", "sex"], as_index=False)["wages_median"]
    .mean()
)
df_wages_grouped["wages_median"] = df_wages_grouped["wages_median"].round(2)

fig = px.bar(
    df_wages_grouped,
    x="ethnicity",
    y="wages_median",
    color="sex",
    barmode="group",
    text_auto=".2f",
    title=f"Median Monthly Wages (RM) by Ethnic Group & Gender ({selected_year})",
    labels={
        "ethnicity": "Ethnic Group",
        "wages_median": "Median Monthly Wage (RM)",
        "sex": "Gender"
    }
)

fig.update_traces(textposition="outside")
fig.update_layout(template="plotly_white", title_x=0.5)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ==========================================
# INTERPRETATION / DISCUSSION
# ==========================================

st.subheader("Interpretation & Discussion")

st.markdown("""
* **Ethnic Wage Disparities:** Distinct wage stratification is observable across ethnic groups, with Chinese and Indian workers generally recording higher median monthly wages compared to Bumiputera and other groups.
* **Gender Pay Gap:** Within almost every ethnic category, male workers consistently earn a higher median monthly wage than female workers, reflecting a persistent structural gender pay gap in the Malaysian labor market.
* **Socioeconomic Meaning:** These disparities highlight differences in occupational distribution, industry concentration, and seniority levels across demographic segments in Malaysia.
""")

# ==========================================
# VIEW DATASET
# ==========================================

with st.expander("View Grouped Wages Dataset"):
    st.dataframe(df_wages_grouped, use_container_width=True)

# ==========================================
# FOOTER
# ==========================================

st.divider()
st.caption("Source: Department of Statistics Malaysia (DOSM)")
st.caption("Malaysia Median Monthly Wages Analysis | Objective 2")
