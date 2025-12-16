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

if "Risk_Level" in df.columns:
    all_risks = sorted(df["Risk_Level"].unique())
    selected_risks = st.sidebar.multiselect("Select Risk Level:", all_risks, default=all_risks)
else:
    selected_risks = [] 

all_years = sorted(df["Year"].unique())
selected_year = st.sidebar.multiselect("Select Year:", all_years, default=all_years)

all_locations = sorted(df["Location"].unique())

# --- CHANGED LINE BELOW: Removed [:10] so it defaults to ALL locations ---
selected_locations = st.sidebar.multiselect("Select Province/City:", all_locations, default=all_locations) 

mask = (df["Year"].isin(selected_year)) & (df["Risk_Level"].isin(selected_risks))

if selected_locations:
    mask = mask & (df["Location"].isin(selected_locations))

df_selection = df[mask]

st.title("🇵🇭 Teenage Pregnancy & Poverty Correlation")
st.markdown("### Topic 12: Correlating Regional Poverty Index with Teenage Birth Rates")
st.markdown("This dashboard analyzes the relationship between socioeconomic factors and adolescent health outcomes.")

col1, col2, col3 = st.columns(3)
if not df_selection.empty:
    avg_poverty = df_selection["Poverty_Incidence"].mean()
    avg_preg = df_selection["Teenage_Birth_Rate"].mean()
else:
    avg_poverty = 0
    avg_preg = 0

col1.metric("Avg. Poverty Incidence", f"{avg_poverty:.1f}%", "Selected Data")
col2.metric("Avg. Teenage Birth Rate", f"{avg_preg:.1f}%", "Prototype Estimate")
col3.metric("Total Records Analyzed", len(df_selection), "Rows")

st.divider()

st.subheader("1. Correlation Analysis: Does Poverty Drive Pregnancy?")
fig_scatter = px.scatter(
    df_selection,
    x="Poverty_Incidence",
    y="Teenage_Birth_Rate",
    color="Risk_Level", 
    size="Poverty_Incidence",
    hover_name="Location",
    title="Poverty Incidence vs. Teenage Birth Rate (Colored by Risk)",
    labels={"Poverty_Incidence": "Poverty Incidence (%)", "Teenage_Birth_Rate": "Teenage Birth Rate (%)"},
    template="plotly_white",
    color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"} 
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.subheader("2. Provincial Comparison")
fig_bar = px.bar(
    df_selection,
    x="Location",
    y="Teenage_Birth_Rate",
    color="Risk_Level", 
    title="Teenage Birth Rates by Province (Colored by Risk Level)",
    template="plotly_white",
    color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"}
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
st.subheader("4. Raw Data Table")
st.dataframe(df_selection, use_container_width=True)

st.divider()
st.caption("Data Source: Philippine Statistics Authority (PSA) - OpenSTAT https://openstat.psa.gov.ph.")
st.caption("Data points correspond to the official PSA Triennial Poverty Release schedule (2018, 2021, 2023).")