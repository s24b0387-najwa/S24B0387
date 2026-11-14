import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="DOSM Correlation Heatmap",
    page_icon="🔥",
    layout="wide"
)

st.title("🔥 Demographic & Economic Indicator Correlation")
st.markdown("Sumber data: **Jabatan Perangkaan Malaysia (DOSM)**")

# Fungsi caching untuk memuat turun data daripada DOSM
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
with st.spinner('Sedang memuat turun dan menggabungkan data daripada DOSM...'):
    df_birth_raw = load_data(URL_BIRTH)
    df_wages_raw = load_data(URL_WAGES)
    df_life_raw = load_data(URL_LIFE)

# ==========================================
# VISUALISASI 3: Correlation Heatmap
# ==========================================
st.header("3. Demographic & Economic Indicator Correlation Heatmap")

# Tapis ke peringkat nasional dan keseluruhan demografi
df_w_nat = df_wages_raw[
    (df_wages_raw['sex'] == 'both') & 
    (df_wages_raw['ethnicity'] == 'overall')
][['date', 'wages_median', 'wages_mean']]

df_b_nat = df_birth_raw[['date', 'abs', 'rate']].rename(
    columns={'abs': 'total_births', 'rate': 'birth_rate'}
)

df_l_nat = df_life_raw[
    (df_life_raw['sex'] == 'both') & 
    (df_life_raw['ethnicity'] == 'overall')
].groupby('date', as_index=False)['life_expectancy'].mean()

# Gabungkan (merge) ketiga-tiga dataset berdasarkan tarikh (date)
df_demographics = pd.merge(df_w_nat, df_b_nat, on='date', how='inner')
df_demographics = pd.merge(df_demographics, df_l_nat, on='date', how='inner')

# Pilih indikator khusus untuk korelasi
indicators = df_demographics[['wages_median', 'wages_mean', 'total_births', 'birth_rate', 'life_expectancy']].rename(
    columns={
        'wages_median': 'Median Monthly Wage',
        'wages_mean': 'Mean Monthly Wage',
        'total_births': 'Total Annual Births',
        'birth_rate': 'Crude Birth Rate',
        'life_expectancy': 'Life Expectancy'
    }
)

# Kira matriks korelasi Pearson
corr_matrix = indicators.corr()

# Cipta heatmap menggunakan px.imshow
fig_corr = px.imshow(
    corr_matrix,
    text_auto='.3f',
    aspect='auto',
    color_continuous_scale='RdBu_r',
    zmin=-1,
    zmax=1,
    title='Demographic & Economic Indicator Correlation Heatmap'
)

# Kemaskan ketinggian carta supaya label mudah dibaca
fig_corr.update_layout(height=600)

# Paparkan graf di Streamlit
st.plotly_chart(fig_corr, use_container_width=True)

# Pilihan untuk melihat jadual matriks korelasi dan data yang digabungkan
with st.expander("Lihat Jadual Matriks Korelasi & Data Gabungan"):
    tab1, tab2 = st.tabs(["Matriks Korelasi (Pearson)", "Data Gabungan (Merged Data)"])
    
    with tab1:
        st.dataframe(corr_matrix.round(3), use_container_width=True)
    with tab2:
        st.dataframe(df_demographics, use_container_width=True)
