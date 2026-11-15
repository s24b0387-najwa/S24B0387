import streamlit as st
import pandas as pd
import plotly.express as px

# Streamlit page configuration
st.set_page_config(
    page_title="DOSM Wages Visualisation",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Median Monthly Wages by Ethnic Group & Gender")
st.markdown("Data source: **Department of Statistics Malaysia (DOSM)**")

# Caching function to load data quickly
@st.cache_data
def load_data(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# DOSM wages dataset URL
URL_WAGES = 'https://storage.dosm.gov.my/labour/wages_ethnicity.parquet'

with st.spinner('Loading wages data from DOSM...'):
    df_wages = load_data(URL_WAGES)

# ==========================================
# VISUALISATION 2: Median Monthly Wages
# ==========================================
st.header("2. Median Monthly Wages (RM) by Ethnic Group & Gender")

# Filter out aggregate categories ('both', 'overall', 'citizen') for a clean comparison
df_wages_clean = df_wages[
    (df_wages['sex'].isin(['male', 'female'])) &
    (~df_wages['ethnicity'].isin(['overall', 'citizen']))
].copy()

# Add interactive selection for time period (All Years or Specific Year)
if 'date' in df_wages_clean.columns:
    df_wages_clean['year'] = df_wages_clean['date'].dt.year
    years = sorted(df_wages_clean['year'].unique(), reverse=True)
    selected_year = st.selectbox(
        "Select Time Period:",
        options=["All Years (Overall Average)"] + [str(y) for y in years]
    )
    
    if selected_year != "All Years (Overall Average)":
        df_wages_clean = df_wages_clean[df_wages_clean['year'] == int(selected_year)]

# Aggregate to find the average median monthly wage by Ethnicity & Gender
df_wages_grouped = df_wages_clean.groupby(['ethnicity', 'sex'], as_index=False)['wages_median'].mean()

# Round values to 2 decimal places for cleaner hover display
df_wages_grouped['wages_median'] = df_wages_grouped['wages_median'].round(2)

# Create bar chart
fig_wages = px.bar(
    df_wages_grouped,
    x='ethnicity',
    y='wages_median',
    color='sex',
    barmode='group',
    text_auto='.2f',
    title=f"Median Monthly Wages (RM) by Ethnic Group & Gender ({selected_year})",
    labels={
        'ethnicity': 'Ethnic Group',
        'wages_median': 'Median Monthly Wage (RM)',
        'sex': 'Gender'
    }
)

# Refine chart layout
fig_wages.update_traces(textposition='outside')
fig_wages.update_layout(yaxis_title="Median Monthly Wage (RM)", xaxis_title="Ethnic Group")

# Display chart in Streamlit
st.plotly_chart(fig_wages, use_container_width=True)

# Option to view processed and raw data tables
with st.expander("View Summary & Raw Data Tables"):
    tab1, tab2 = st.tabs(["Summary Data (Grouped)", "Raw Data (Cleaned)"])
    
    with tab1:
        st.dataframe(df_wages_grouped, use_container_width=True)
    with tab2:
        st.dataframe(df_wages_clean, use_container_width=True)
