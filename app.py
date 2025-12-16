import streamlit as st
import pandas as pd
import plotly.express as px

# 1. MOBILE TWEAK: Set layout to wide, but it auto-adjusts on phones
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

# --- SIDEBAR ---
st.sidebar.header("Filter Options")
st.sidebar.info("On Mobile? Tap the arrow '>' at the top left to open filters.") # 2. MOBILE TWEAK: Help text

if "Risk_Level" in df.columns:
    all_risks = sorted(df["Risk_Level"].unique())
    selected_risks = st.sidebar.multiselect("Select Risk Level:", all_risks, default=all_risks)
else:
    selected_risks = [] 

all_years = sorted(df["Year"].unique())
selected_year = st.sidebar.multiselect("Select Year:", all_years, default=all_years)

all_locations = sorted(df["Location"].unique())
selected_locations = st.sidebar.multiselect("Select Province/City:", all_locations, default=all_locations) 

mask = (df["Year"].isin(selected_year)) & (df["Risk_Level"].isin(selected_risks))
if selected_locations:
    mask = mask & (df["Location"].isin(selected_locations))

df_selection = df[mask]

# --- MAIN PAGE ---
st.title("🇵🇭 Teenage Pregnancy & Poverty Correlation")
st.markdown("### Topic 12: Correlating Regional Poverty Index with Teenage Birth Rates")

col1, col2, col3 = st.columns(3)
if not df_selection.empty:
    avg_poverty = df_selection["Poverty_Incidence"].mean()
    avg_preg = df_selection["Teenage_Birth_Rate"].mean()
else:
    avg_poverty = 0
    avg_preg = 0

col1.metric("Avg. Poverty", f"{avg_poverty:.1f}%")
col2.metric("Avg. Birth Rate", f"{avg_preg:.1f}%")
col3.metric("Records", len(df_selection))

st.divider()

# --- CHART 1: SCATTER (Auto-resizes on mobile) ---
st.subheader("1. Correlation Analysis")
fig_scatter = px.scatter(
    df_selection,
    x="Poverty_Incidence",
    y="Teenage_Birth_Rate",
    color="Risk_Level", 
    size="Poverty_Incidence",
    hover_name="Location",
    title="Poverty vs. Pregnancy (Tap dots for info)",
    template="plotly_white",
    color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"} 
)
# Move legend to top for mobile to save horizontal space
fig_scatter.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_scatter, use_container_width=True)

# --- CHART 2: BAR CHART (MOBILE OPTIMIZED) ---
st.subheader("2. Provincial Comparison")

# 3. MOBILE TWEAK: Calculate height based on number of bars
# If we have 80 provinces, make the chart 2000px tall so it's readable!
num_locations = len(df_selection["Location"].unique())
dynamic_height = max(500, num_locations * 25) # Minimum 500px, or 25px per province

fig_bar = px.bar(
    df_selection,
    y="Location",  # <--- Put Location on Y-Axis (Horizontal Bar)
    x="Teenage_Birth_Rate", # <--- Put Value on X-Axis
    color="Risk_Level", 
    orientation='h', # <--- Crucial for Mobile: Makes it scrollable
    height=dynamic_height, # <--- Apply dynamic height
    title="Teenage Birth Rates (Scroll down to see all)",
    template="plotly_white",
    color_discrete_map={"Low": "green", "Medium": "orange", "High": "red"}
)
# Sort bars so the longest are at the top
fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_bar, use_container_width=True)

# --- CHART 3: TRENDS ---
st.subheader("3. Yearly Trends")
df_trend = df_selection.groupby("Year")[["Poverty_Incidence", "Teenage_Birth_Rate"]].mean().reset_index()

fig_line = px.line(
    df_trend,
    x="Year",
    y=["Poverty_Incidence", "Teenage_Birth_Rate"],
    markers=True,
    title="Average Trends (2018-2023)",
    template="plotly_white"
)
fig_line.update_xaxes(dtick=1)
# Move legend to top
fig_line.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
st.plotly_chart(fig_line, use_container_width=True)

st.divider()
st.subheader("4. Raw Data Table")
st.dataframe(df_selection, use_container_width=True)

st.caption("Data Source: PSA OpenSTAT | Note: Prototype Demo")