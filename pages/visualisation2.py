import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit page configuration
st.set_page_config(
    page_title="DOSM Wages Visualisation",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Median Monthly Wages Analysis in Malaysia")
st.markdown("Data source: **Department of Statistics Malaysia (DOSM)**")

# Caching function to load data quickly
@st.cache_data
def load_data(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

URL_WAGES = 'https://storage.dosm.gov.my/labour/wages_ethnicity.parquet'

with st.spinner('Loading wages data from DOSM...'):
    df_wages = load_data(URL_WAGES)

# Clean data (exclude aggregate categories)
df_wages_clean = df_wages[
    (df_wages['sex'].isin(['male', 'female'])) &
    (~df_wages['ethnicity'].isin(['overall', 'citizen']))
].copy()
df_wages_clean['year'] = df_wages_clean['date'].dt.year

# Sidebar filter
st.sidebar.header("Dashboard Filters")
years = sorted(df_wages_clean['year'].unique(), reverse=True)
selected_year = st.sidebar.selectbox(
    "Select Time Period (for Chart 1 & Summary):",
    options=["All Years (Overall Average)"] + [str(y) for y in years]
)

if selected_year != "All Years (Overall Average)":
    df_filtered = df_wages_clean[df_wages_clean['year'] == int(selected_year)]
else:
    df_filtered = df_wages_clean.copy()

st.divider()

# ==========================================
# 1. OBJECTIVE STATEMENT
# ==========================================
st.subheader("1. Objective Statement")
st.info(
    "This page aims to examine disparities in median monthly wages across major ethnic groups and genders in Malaysia. "
    "It further evaluates longitudinal wage growth trends and income dispersion over time."
)

# ==========================================
# 2. SUMMARY BOX
# ==========================================
st.subheader("2. Summary Box")

overall_median = df_filtered['wages_median'].mean()
male_median = df_filtered[df_filtered['sex'] == 'male']['wages_median'].mean()
female_median = df_filtered[df_filtered['sex'] == 'female']['wages_median'].mean()
gender_gap = male_median - female_median

col1, col2, col3, col4 = st.columns(4)
col1.metric("Average Median Wage", f"RM {overall_median:,.2f}")
col2.metric("Male Median Wage", f"RM {male_median:,.2f}")
col3.metric("Female Median Wage", f"RM {female_median:,.2f}")
col4.metric("Gender Wage Gap (M - F)", f"RM {gender_gap:,.2f}")

st.divider()

# ==========================================
# 3. VISUALIZATIONS (3 PER PAGE)
# ==========================================
st.subheader("3. Scientific Visualizations")

# --- Visualization 1: Grouped Bar Chart ---
df_wages_grouped = df_filtered.groupby(['ethnicity', 'sex'], as_index=False)['wages_median'].mean()
df_wages_grouped['wages_median'] = df_wages_grouped['wages_median'].round(2)

fig1 = px.bar(
    df_wages_grouped,
    x='ethnicity',
    y='wages_median',
    color='sex',
    barmode='group',
    text_auto='.2f',
    title=f"Visualization 1: Median Monthly Wages (RM) by Ethnic Group & Gender ({selected_year})",
    labels={'ethnicity': 'Ethnic Group', 'wages_median': 'Median Monthly Wage (RM)', 'sex': 'Gender'}
)
fig1.update_traces(textposition='outside')
fig1.update_layout(template="plotly_white")
st.plotly_chart(fig1, use_container_width=True)

# --- Visualization 2 & 3 in 2 Columns ---
viz_col1, viz_col2 = st.columns(2)

with viz_col1:
    # Visualization 2: Line Plot (Temporal Trend across Ethnicities)
    df_trend = df_wages_clean.groupby(['date', 'ethnicity'], as_index=False)['wages_median'].mean()
    fig2 = px.line(
        df_trend,
        x='date',
        y='wages_median',
        color='ethnicity',
        markers=True,
        title="Visualization 2: Longitudinal Trend of Median Wages by Ethnicity",
        labels={'date': 'Year', 'wages_median': 'Median Monthly Wage (RM)', 'ethnicity': 'Ethnic Group'}
    )
    fig2.update_layout(template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

with viz_col2:
    # Visualization 3: Box Plot (Wage Distribution & Dispersion)
    fig3 = px.box(
        df_wages_clean,
        x='ethnicity',
        y='wages_median',
        color='sex',
        title="Visualization 3: Wage Distribution & Variability by Ethnicity and Gender",
        labels={'ethnicity': 'Ethnic Group', 'wages_median': 'Median Monthly Wage (RM)', 'sex': 'Gender'}
    )
    fig3.update_layout(template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ==========================================
# 4. INTERPRETATION / DISCUSSION
# ==========================================
st.subheader("4. Interpretation & Discussion")
st.markdown("""
* **Observed Patterns & Disparities:** Across all observed periods, distinct wage stratification exists among ethnic groups, with Chinese and Indian workers generally recording higher median monthly wages compared to Bumiputera and other groups. Within almost every ethnic category, male workers consistently earn a higher median wage than female workers, reflecting a persistent structural gender pay gap.
* **Temporal Trajectory & Anomalies:** The longitudinal line plot demonstrates a steady upward trajectory in nominal median wages over time due to economic growth and minimum wage revisions, punctuated by brief stagnation or dips during macroeconomic disruptions (such as the 2020–2021 pandemic period).
* **Scientific & Socioeconomic Meaning:** The box plot spread indicates greater interquartile variance in higher-earning ethnic groups, suggesting wider occupational dispersion across high-skilled and entry-level roles. Scientifically, these distributions highlight how demographic segmentation intersects with labor market outcomes in Malaysia.
""")

# Optional Raw Data Expander
with st.expander("View Processed & Raw Wages Data"):
    tab1, tab2 = st.tabs(["Grouped Summary Data", "Cleaned Dataset"])
    with tab1:
        st.dataframe(df_wages_grouped, use_container_width=True)
    with tab2:
        st.dataframe(df_wages_clean, use_container_width=True)
