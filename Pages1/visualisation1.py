import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Malaysia Demographic Analysis",
    page_icon="📊",
    layout="wide"
)

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
# SIDEBAR NAVIGATION
# ==========================================

st.sidebar.title("Dashboard Navigation")

selected_page = st.sidebar.radio(
    "Select Research Objective",
    [
        "Objective 1 - Live Birth Analysis",
        "Objective 2 - Life Expectancy and Income"
    ]
)

st.sidebar.divider()


# ==========================================
# DATASET URLS
# ==========================================

BIRTH_URL = (
    "https://storage.dosm.gov.my/demography/birth.parquet"
)

LIFE_URL = (
    "https://storage.dosm.gov.my/demography/"
    "life_expectancy.parquet"
)

WAGES_URL = (
    "https://storage.dosm.gov.my/labour/"
    "wages_ethnicity.parquet"
)


# ==========================================
# LOAD DATASETS
# ==========================================

@st.cache_data
def load_birth_data():

    df = pd.read_parquet(BIRTH_URL)

    df["date"] = pd.to_datetime(df["date"])

    return df


@st.cache_data
def load_life_wages_data():

    df_life = pd.read_parquet(LIFE_URL)
    df_wages = pd.read_parquet(WAGES_URL)

    return df_life, df_wages


# ==========================================
# OBJECTIVE 1
# LIVE BIRTH ANALYSIS
# ==========================================

if selected_page == "Objective 1 - Live Birth Analysis":

    try:
        df_birth = load_birth_data()

    except Exception as e:
        st.error(f"Unable to load birth dataset: {e}")
        st.stop()

    # Dashboard Header

    st.title("Malaysia Live Birth Analysis")

    st.markdown(
        '<p class="subtitle">'
        'Exploring live birth trends in Malaysia from 2000 to 2025.'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()

    # Research Objective

    st.subheader("Research Objective 1")

    st.info(
        "Examine the trends in live births in Malaysia "
        "over the years."
    )

    # Year Filter

    st.sidebar.subheader("Dashboard Filters")

    min_year = int(df_birth["date"].dt.year.min())
    max_year = int(df_birth["date"].dt.year.max())

    year_range = st.sidebar.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1,
        key="birth_year_range"
    )

    start_year, end_year = year_range

    # Filter Data

    df_filtered = df_birth[
        (df_birth["date"].dt.year >= start_year) &
        (df_birth["date"].dt.year <= end_year)
    ].copy()

    # Group by Year

    df_annual = (
        df_filtered
        .groupby(df_filtered["date"].dt.year)["abs"]
        .sum()
        .reset_index()
    )

    df_annual.columns = ["Year", "Total Births"]

    df_annual = df_annual.sort_values("Year")

    if df_annual.empty:
        st.warning("No data available for the selected year range.")
        st.stop()

    # Summary Metrics

    total_births = df_annual["Total Births"].sum()

    average_births = df_annual["Total Births"].mean()

    latest_births = df_annual.iloc[-1]["Total Births"]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Live Births",
        f"{total_births:,.0f}"
    )

    col2.metric(
        "Average Annual Births",
        f"{average_births:,.0f}"
    )

    col3.metric(
        f"Live Births in {int(df_annual.iloc[-1]['Year'])}",
        f"{latest_births:,.0f}"
    )

    st.divider()

    # Visualization 1 - Line Chart

    st.subheader("Total Annual Live Births in Malaysia")

    st.write(
        "This line chart illustrates the changes in the total "
        "number of live births in Malaysia over the selected years. "
        "It helps identify the overall trend and fluctuations "
        "in annual live births."
    )

    fig = px.line(
        df_annual,
        x="Year",
        y="Total Births",
        markers=True,
        title="Total Annual Live Births in Malaysia",
        labels={
            "Year": "Year",
            "Total Births": "Total Live Births"
        }
    )

    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=7)
    )

    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Year",
        yaxis_title="Total Live Births",
        title_x=0.5
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # View Dataset

    with st.expander("View Annual Birth Dataset"):

        st.dataframe(
            df_annual,
            use_container_width=True
        )

    # Footer

    st.divider()

    st.caption(
        "Source: Department of Statistics Malaysia (DOSM)"
    )

    st.caption(
        "Malaysia Live Birth Analysis | Objective 1"
    )


# ==========================================
# OBJECTIVE 2
# LIFE EXPECTANCY AND INCOME ANALYSIS
# ==========================================

elif selected_page == "Objective 2 - Life Expectancy and Income":

    try:
        df_life, df_wages = load_life_wages_data()

    except Exception as e:
        st.error(f"Unable to load datasets: {e}")
        st.stop()

    # Clean Life Expectancy Data

    df_life_clean = df_life[
        (df_life["sex"].isin(["male", "female"])) &
        (~df_life["ethnicity"].isin(["overall", "citizen"]))
    ].copy()

    # Clean Wages Data

    df_wages_clean = df_wages[
        (df_wages["sex"].isin(["male", "female"])) &
        (~df_wages["ethnicity"].isin(["overall", "citizen"]))
    ].copy()

    # Group Data

    df_life_grouped = (
        df_life_clean
        .groupby(["ethnicity", "sex"], as_index=False)
        ["life_expectancy"].mean()
    )

    df_wages_grouped = (
        df_wages_clean
        .groupby(["ethnicity", "sex"], as_index=False)
        ["wages_median"].mean()
    )

    # Merge Datasets

    df_combined = pd.merge(
        df_life_grouped,
        df_wages_grouped,
        on=["ethnicity", "sex"],
        how="inner"
    )

    if df_combined.empty:
        st.warning("No matching data found.")
        st.stop()

    # Dashboard Header

    st.title("Life Expectancy and Income Analysis")

    st.markdown(
        '<p class="subtitle">'
        'Comparing life expectancy and median monthly wages '
        'among different ethnic groups and genders in Malaysia.'
        '</p>',
        unsafe_allow_html=True
    )

    st.divider()

    # Research Objective

    st.subheader("Research Objective 2")

    st.info(
        "Compare life expectancy and income among different "
        "ethnic groups and genders in Malaysia to identify "
        "existing differences and gaps."
    )

    # Sidebar Filters

    st.sidebar.subheader("Dashboard Filters")

    st.sidebar.markdown("### Gender")

    gender_options = [
        "All Genders",
        "Male",
        "Female"
    ]

    selected_gender = st.sidebar.selectbox(
        "Select Gender",
        gender_options,
        key="life_gender"
    )

    st.sidebar.markdown("### Ethnic Group")

    ethnicity_options = sorted(
        df_combined["ethnicity"].unique()
    )

    selected_ethnicity = st.sidebar.selectbox(
        "Select Ethnic Group",
        ["All Ethnic Groups"] + ethnicity_options,
        key="life_ethnicity"
    )

    # Apply Filters

    df_display = df_combined.copy()

    if selected_gender != "All Genders":

        df_display = df_display[
            df_display["sex"] == selected_gender.lower()
        ]

    if selected_ethnicity != "All Ethnic Groups":

        df_display = df_display[
            df_display["ethnicity"] == selected_ethnicity
        ]

    # Check Filter Results

    if df_display.empty:

        st.warning("No data available for the selected filters.")

    else:

        # Summary Metrics

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Ethnic-Gender Groups",
            f"{len(df_display)}"
        )

        col2.metric(
            "Average Life Expectancy",
            f"{df_display['life_expectancy'].mean():.2f} years"
        )

        col3.metric(
            "Average Monthly Wage",
            f"RM {df_display['wages_median'].mean():,.2f}"
        )

        st.divider()

        # Visualization 2 - Scatter Plot

        st.subheader(
            "Life Expectancy vs Median Monthly Wages"
        )

        st.write(
            "This scatter plot compares average life expectancy "
            "and median monthly wages among different ethnic groups "
            "and genders in Malaysia. Each point represents an "
            "ethnic group and gender combination."
        )

        fig = px.scatter(
            df_display,
            x="wages_median",
            y="life_expectancy",
            color="sex",
            symbol="ethnicity",
            hover_name="ethnicity",
            hover_data={
                "sex": True,
                "wages_median": ":,.2f",
                "life_expectancy": ":.2f"
            },
            title="Life Expectancy vs Median Monthly Wages",
            labels={
                "wages_median": "Average Median Monthly Wage (RM)",
                "life_expectancy": "Average Life Expectancy (Years)",
                "sex": "Gender",
                "ethnicity": "Ethnic Group"
            }
        )

        fig.update_traces(
            marker=dict(
                size=13,
                opacity=0.8
            )
        )

        fig.update_layout(
            template="plotly_white",
            title_x=0.5,
            hovermode="closest"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # View Combined Dataset

        with st.expander("View Combined Dataset"):

            st.dataframe(
                df_display,
                use_container_width=True
            )

    # Footer

    st.divider()

    st.caption(
        "Data Sources: Department of Statistics Malaysia (DOSM)"
    )

    st.caption(
        "Life Expectancy and Income Analysis | Objective 2"
    )
