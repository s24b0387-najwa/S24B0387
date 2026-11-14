import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION (HANYA SEKALI DI SINI)
# ==========================================

st.set_page_config(
    page_title="Scientific Visualization",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# HEADER & PLO METRICS (DARI MAIN ASAL ANDA)
# ==========================================

st.header("Scientific Visualization", divider="gray")

col1, col2, col3, col4 = st.columns(4)

col1.metric(label="PLO 2", value="3.3", help="PLO 2: Cognitive Skill", border=True)
col2.metric(label="PLO 3", value="3.5", help="PLO 3: Digital Skill", border=True)
col3.metric(label="PLO 4", value="4.0", help="PLO 4: Interpersonal Skill", border=True)
col4.metric(label="PLO 5", value="4.3", help="PLO 5: Communication Skill", border=True)

st.divider()

# ==========================================
# VISUALISATION 1: ARTS FACULTY GENDER ANALYSIS
# ==========================================

st.header("Arts Faculty Gender Distribution Analysis 🎨", divider="gray")

url = "https://raw.githubusercontent.com/fakhitah3/SV2025/refs/heads/main/arts_faculty_data.csv"

try:
    arts_df = pd.read_csv(url)
    st.success("Data loaded successfully!")

    st.subheader("Raw Data Preview")
    st.dataframe(arts_df.head(), use_container_width=True)

    gender_counts = arts_df['Gender'].value_counts().reset_index()
    gender_counts.columns = ['Gender', 'Count']

    st.subheader("Gender Distribution in Arts Faculty")

    fig_arts = px.pie(
        gender_counts,
        values='Count',
        names='Gender',
        title='Distribution of Gender in Arts Faculty',
        color_discrete_sequence=px.colors.sequential.Agsunset,
        hover_data=['Count'],
        labels={'Count': 'Number of Students'}
    )

    fig_arts.update_traces(textposition='inside', textinfo='percent+label')
    fig_arts.update_layout(showlegend=True)

    st.plotly_chart(fig_arts, use_container_width=True)

except Exception as e:
    st.error(f"Error loading or processing Arts Faculty data: {e}")

st.divider()

# ==========================================
# VISUALISATION 1 (DOSM): MALAYSIA LIVE BIRTHS
# ==========================================

st.header("Malaysia Live Birth Analysis (Objective 1)", divider="gray")

BIRTH_URL = "https://dosm.gov.my"

@st.cache_data
def load_birth_data():
    df = pd.read_parquet(BIRTH_URL)
    df["date"] = pd.to_datetime(df["date"])
    if "sex" in df.columns:
        df = df[df["sex"] == "both"]
    if "state" in df.columns:
        df = df[df["state"] == "Malaysia"]
    return df

try:
    df_birth = load_birth_data()

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

    df_filtered = df_birth[
        (df_birth["date"].dt.year >= year_range[0]) &
        (df_birth["date"].dt.year <= year_range[1])
    ].copy()

    df_annual = (
        df_filtered.groupby(df_filtered["date"].dt.year)["abs"]
        .sum()
        .reset_index()
    )
    df_annual.columns = ["Year", "Total Births"]
    df_annual = df_annual.sort_values("Year")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Live Births", f"{df_annual['Total Births'].sum():,.0f}")
    c2.metric("Average Annual Births", f"{df_annual['Total Births'].mean():,.0f}")
    c3.metric(
        f"Live Births in {int(df_annual.iloc[-1]['Year'])}",
        f"{df_annual.iloc[-1]['Total Births']:,.0f}"
    )

    fig_birth = px.line(
        df_annual,
        x="Year",
        y="Total Births",
        markers=True,
        title="Total Annual Live Births in Malaysia",
        labels={"Year": "Year", "Total Births": "Total Live Births"}
    )
    fig_birth.update_traces(line=dict(width=3), marker=dict(size=7))
    fig_birth.update_layout(template="plotly_white", hovermode="x unified", title_x=0.5)

    st.plotly_chart(fig_birth, use_container_width=True)

except Exception as e:
    st.error(f"Unable to load birth dataset: {e}")
