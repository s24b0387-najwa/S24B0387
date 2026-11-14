import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="DOSM Wages Visualisation",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Median Monthly Wages by Ethnic Group & Gender")
st.markdown("Sumber data: **Jabatan Perangkaan Malaysia (DOSM)**")

# Fungsi caching untuk memuat turun data dengan pantas
@st.cache_data
def load_data(url):
    df = pd.read_parquet(url)
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
    return df

# URL dataset wages daripada DOSM
URL_WAGES = 'https://storage.dosm.gov.my/labour/wages_ethnicity.parquet'

with st.spinner('Sedang memuat turun data gaji daripada DOSM...'):
    df_wages = load_data(URL_WAGES)

# ==========================================
# VISUALISASI 2: Median Monthly Wages
# ==========================================
st.header("2. Median Monthly Wages (RM) by Ethnic Group & Gender")

# Tapis kategori agregat ('both', 'overall', 'citizen') untuk perbandingan yang bersih
df_wages_clean = df_wages[
    (df_wages['sex'].isin(['male', 'female'])) &
    (~df_wages['ethnicity'].isin(['overall', 'citizen']))
].copy()

# Tambah pilihan interaktif untuk memilih tempoh masa (Semua Tahun atau Tahun Tertentu)
if 'date' in df_wages_clean.columns:
    df_wages_clean['year'] = df_wages_clean['date'].dt.year
    years = sorted(df_wages_clean['year'].unique(), reverse=True)
    selected_year = st.selectbox(
        "Pilih Tempoh Masa:",
        options=["Semua Tahun (Purata Keseluruhan)"] + [str(y) for y in years]
    )
    
    if selected_year != "Semua Tahun (Purata Keseluruhan)":
        df_wages_clean = df_wages_clean[df_wages_clean['year'] == int(selected_year)]

# Agregat untuk mendapatkan purata gaji median bulanan mengikut Etnik & Jantina
df_wages_grouped = df_wages_clean.groupby(['ethnicity', 'sex'], as_index=False)['wages_median'].mean()

# Bundarkan nilai kepada 2 tempat perpuluhan supaya kemas apabila hover
df_wages_grouped['wages_median'] = df_wages_grouped['wages_median'].round(2)

# Cipta carta palang (bar chart)
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

# Kemaskan susun atur graf
fig_wages.update_traces(textposition='outside')
fig_wages.update_layout(yaxis_title="Median Monthly Wage (RM)", xaxis_title="Ethnic Group")

# Paparkan graf di Streamlit
st.plotly_chart(fig_wages, use_container_width=True)

# Pilihan untuk melihat jadual data yang telah diproses
with st.expander("Lihat Jadual Data Ringkasan & Data Mentah"):
    tab1, tab2 = st.tabs(["Data Ringkasan (Grouped)", "Data Mentah (Cleaned)"])
    
    with tab1:
        st.dataframe(df_wages_grouped, use_container_width=True)
    with tab2:
        st.dataframe(df_wages_clean, use_container_width=True)
