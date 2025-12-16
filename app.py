import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Teenage Pregnancy & Poverty Dashboard", layout="wide")

@st.cache_data
def load_data():
    data = pd.read_csv("teenage_pregnancy_poverty_merged.csv")
    return data

try:
    df = load_data()
except FileNotFoundError:
    st.error("File not found! Please make sure 'teenage_pregnancy_poverty_merged.csv' is in the same folder.")
    st.stop()

st.sidebar.header("Filter Options")
st.sidebar.write("Customize your view below:")

all_years = sorted(df["Year"].unique())
selected_year = st.sidebar.multiselect("Select Year:", all_years, default=all_years)

all_locations = sorted(df["Location"].unique())
selected_locations = st.sidebar.multiselect("Select Province/City:", all_locations, default=all_locations[:10]) # Default to first 10

if not selected_locations:
    df_selection = df.query("Year == @selected_year")
else:
    df_selection = df.query("Year == @selected_year & Location == @selected_locations")

st.title("🇵🇭 Teenage Pregnancy & Poverty Correlation")
st.markdown("### Topic 12: Correlating Regional Poverty Index with Teenage Birth Rates")
st.markdown("This dashboard analyzes the relationship between socioeconomic factors and adolescent health outcomes.")

col1, col2, col3 = st.columns(3)
avg_poverty = df_selection["Poverty_Incidence"].mean()
avg_preg = df_selection["Teenage_Birth_Rate"].mean()

col1.metric("Avg. Poverty Incidence", f"{avg_poverty:.1f}%", "Selected Data")
col2.metric("Avg. Teenage Birth Rate", f"{avg_preg:.1f}%", "Prototype Estimate")
col3.metric("Total Records Analyzed", len(df_selection), "Rows")

st.divider()

st.subheader("1. Correlation Analysis: Does Poverty Drive Pregnancy?")
fig_scatter = px.scatter(
    df_selection,
    x="Poverty_Index" if "Poverty_Index" in df_selection.columns else "Poverty_Incidence",
    y="Teenage_Birth_Rate",
    color="Year",
    size="Poverty_Incidence",
    hover_name="Location",
    title="Poverty Incidence vs. Teenage Birth Rate",
    labels={"Poverty_Incidence": "Poverty Incidence (%)", "Teenage_Birth_Rate": "Teenage Birth Rate (%)"},
    template="plotly_white"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("2. Provincial Comparison")
fig_bar = px.bar(
    df_selection,
    x="Location",
    y="Teenage_Birth_Rate",
    color="Poverty_Incidence",
    title="Teenage Birth Rates by Province (Colored by Poverty Level)",
    template="plotly_white"
)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("3. Yearly Trends")
df_trend = df_selection.groupby("Year")[["Poverty_Incidence", "Teenage_Birth_Rate"]].mean().reset_index()

fig_line = px.line(
    df_trend,
    x="Year",
    y=["Poverty_Incidence", "Teenage_Birth_Rate"],
    markers=True,
    title="Average Trends Over Time (2018 - 2023)",
    template="plotly_white"
)
st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.caption("Data Source: Philippine Statistics Authority (PSA) - OpenSTAT https://openstat.psa.gov.ph | Note: Pregnancy data is simulated for prototype demonstration.")
st.caption("Data points correspond to the official PSA Triennial Poverty Release schedule (2018, 2021, 2023).")