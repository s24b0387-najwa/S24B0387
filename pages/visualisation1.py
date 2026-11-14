import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="DOSM Data Visualisation",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Malaysia Demographic & Labour Visualisation")
st.markdown("Sumber data: **Jabatan Perangkaan Malaysia (DOSM)**")

# Fungsi untuk memuat turun data dengan caching supaya aplikasi lebih laju
@st.cache_data
def load_data(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# URL dataset daripada DOSM
URL_BIRTH = 'https://storage.dosm.gov.my/demography/birth.parquet'
URL_WAGES = 'https://storage.dosm.gov.my/labour/wages_ethnicity.parquet'
URL_LIFE = 'https://storage.dosm.gov.my/demography/life_expectancy_state_ethnic.parquet'

# Memuatkan semua dataset
with st.spinner('Sedang memuat turun data daripada DOSM...'):
    df_birth = load_data(URL_BIRTH)
    df_wages = load_data(URL_WAGES)
    df_life = load_data(URL_LIFE)

# ==========================================
# VISUALISASI 1: Jumlah Kelahiran Hidup (Births)
# ==========================================
st.header("1. Total Annual Live Births in Malaysia (2000-2025)")

# Filter dataset antara tahun 2000 hingga 2025
df_birth_all = df_birth[
    (df_birth['date'] >= '2000-01-01') & 
    (df_birth['date'] <= '2025-12-31')
]

# Cipta graf garis Plotly
fig_birth = px.line(
    df_birth_all,
    x='date',
    y='abs',
    title="Total Annual Live Births in Malaysia (2000-2025)",
    labels={'date': 'Year', 'abs': 'Total Live Births'},
    markers=True
)

# Paparkan graf di Streamlit
st.plotly_chart(fig_birth, use_container_width=True)

# Pilihan untuk melihat data mentah (Dataframe)
with st.expander("Lihat Jadual Data (Raw Data)"):
    tab1, tab2, tab3 = st.tabs(["Birth Data", "Wages by Ethnicity", "Life Expectancy"])
    
    with tab1:
        st.dataframe(df_birth_all, use_container_width=True)
    with tab2:
        st.dataframe(df_wages, use_container_width=True)
    with tab3:
        st.dataframe(df_life, use_container_width=True)
