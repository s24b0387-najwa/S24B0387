import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# LIGHT THEME (SERAGAM DENGAN MAIN.PY)
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
    "Examine disparities in median monthly wages across major ethnic groups and genders in Malaysia, "
    "and evaluate longitudinal wage trends and dispersion over time."
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
# VISUALIZATION 1 - GROUPED BAR CHART
# ==========================================

st.subheader("1. Median Monthly Wages (RM) by Ethnic Group & Gender")

st.write(
    "This grouped bar chart compares the average median monthly wages between male and female "
    "workers across major ethnic groups in Malaysia for the selected period."
)

df_wages_grouped = (
    df_filtered
    .groupby(["ethnicity", "sex"], as_index=False)["wages_median"]
    .mean()
)
df_wages_grouped["wages_median"] = df_wages_grouped["wages_median"].round(2)

fig1 = px.bar(
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

fig1.update_traces(textposition="outside")
fig1.update_layout(template="plotly_white", title_x=0.5)

st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ==========================================
# VISUALIZATION 2 & 3 (3 VISUALIZATIONS PER PAGE)
# ==========================================

viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    st.subheader("2. Longitudinal Wage Trend by Ethnicity")
    st.write(
        "This line plot tracks the progression of median monthly wages across ethnic groups over time."
    )
    df_trend = (
        df_wages_clean
        .groupby(["date", "ethnicity"], as_index=False)["wages_median"]
        .mean()
    )
    fig2 = px.line(
        df_trend,
        x="date",
        y="wages_median",
        color="ethnicity",
        markers=True,
        title="Median Monthly Wage Trend Over Time",
        labels={
            "date": "Year",
            "wages_median": "Median Monthly Wage (RM)",
            "ethnicity": "Ethnic Group"
        }
    )
    fig2.update_traces(line=dict(width=2.5), marker=dict(size=6))
    fig2.update_layout(template="plotly_white", hovermode="x unified", title_x=0.5)
    st.plotly_chart(fig2, use_container_width=True)

with viz_col2:
    st.subheader("3. Wage Distribution & Dispersion")
    st.write(
        "This box plot illustrates the statistical spread, median, and interquartile range of wages across groups."
    )
    fig3 = px.box(
        df_wages_clean,
        x="ethnicity",
        y="wages_median",
        color="sex",
        title="Wage Distribution by Ethnic Group & Gender",
        labels={
            "ethnicity": "Ethnic Group",
            "wages_median": "Median Monthly Wage (RM)",
            "sex": "Gender"
        }
    )
    fig3.update_layout(template="plotly_white", title_x=0.5)
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ==========================================
# INTERPRETATION / DISCUSSION
# ==========================================

st.subheader("Interpretation & Discussion")

st.markdown("""
* **Observed Patterns & Disparities:** Distinct wage stratification is evident across ethnic groups, with Chinese and Indian workers consistently recording higher median monthly wages than Bumiputera and other groups. Across nearly all ethnic categories, male workers earn a higher median wage than female workers, reflecting a persistent structural gender pay gap.
* **Temporal Trajectory & Anomalies:** The longitudinal line plot shows a steady upward trend in nominal median wages over the years driven by economic expansion and minimum wage policies, with temporary stagnation during macroeconomic shocks such as the 2020–2021 pandemic period.
* **Scientific & Socioeconomic Meaning:** The wider interquartile range observed in higher-earning ethnic groups indicates greater occupational dispersion across high-skilled and entry-level sectors, demonstrating how demographic factors intersect with labor market segmentation in Malaysia.
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
