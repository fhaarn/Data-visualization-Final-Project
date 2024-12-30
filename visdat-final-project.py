import streamlit as st
import pandas as pd
import plotly.express as px

# Title and Introduction
st.title("World GDP per Capita Visualization")
st.markdown("""
This interactive application visualizes the global GDP per capita for selected years.
Darker colors indicate higher GDP values. Data is enriched with income group and region information.
""")

# File paths
api_ny_path = "API_NY.GDP.PCAP.CD_DS2_en_csv_v2_76.csv"
metadata_path = "Metadata_Country_API_NY.GDP.PCAP.CD_DS2_en_csv_v2_76.csv"

# Load the datasets
api_ny = pd.read_csv(api_ny_path, skiprows=4)
metadata = pd.read_csv(metadata_path)

# Merge the datasets
metadata = metadata[['Country Code', 'IncomeGroup', 'Region']]  # Include Region and IncomeGroup
merged_df = pd.merge(
    api_ny,
    metadata,
    left_on='Country Code',
    right_on='Country Code',
    how='left'
)

# Ensure all year columns are numeric
year_columns = [str(year) for year in range(1960, 2024)]
for year in year_columns:
    merged_df[year] = pd.to_numeric(merged_df[year], errors='coerce')

# Add your name to the sidebar
st.sidebar.markdown("**Created by: Muhammad Farhan Audianto**")

# Sidebar filters
st.sidebar.header("Filters")

# IncomeGroup dropdown
income_groups = ["All"] + sorted(merged_df['IncomeGroup'].dropna().unique().tolist())
selected_income_group = st.sidebar.selectbox("Select Income Group", income_groups)

# Region dropdown
regions = ["All"] + sorted(merged_df['Region'].dropna().unique().tolist())
selected_region = st.sidebar.selectbox("Select Region", regions)

# Slider to select year (moved to the sidebar)
selected_year = st.sidebar.slider("Select a year for visualization:", 1960, 2023, 2023)

# Filter the data based on sidebar dropdowns for IncomeGroup and Region
filtered_df_sidebar = merged_df.copy()

if selected_income_group != "All":
    filtered_df_sidebar = filtered_df_sidebar[filtered_df_sidebar['IncomeGroup'] == selected_income_group]

if selected_region != "All":
    filtered_df_sidebar = filtered_df_sidebar[filtered_df_sidebar['Region'] == selected_region]

# Display the dataset
if st.checkbox("Show Dataset"):
    filtered_columns = ['Country Name'] + [str(year) for year in range(1960, 2024)]  # Include years 1960 to 2023
    filtered_df = filtered_df_sidebar[filtered_columns]
    st.write("Dataset (GDP per capita (current US$))", filtered_df)

# Choropleth Map
st.subheader(f"World Map of GDP per Capita ({selected_year})")
fig = px.choropleth(
    filtered_df_sidebar,
    locations='Country Code',
    color=str(selected_year),  # Use the selected year dynamically
    hover_name='Country Name',
    hover_data=['Region', 'IncomeGroup'],
    title=f'GDP per Capita ({selected_year})',
    color_continuous_scale=px.colors.sequential.Plasma
)
fig.update_layout(
    geo=dict(showframe=False, showcoastlines=True, projection_type='equirectangular'),
    width=1500,  # Adjust width
    height=700   # Adjust height
)
st.plotly_chart(fig, use_container_width=False)

# Highlight top and bottom countries
st.subheader(f"Top and Bottom Countries by GDP ({selected_year})")

# Get top 5 and bottom 5 countries
top_5_countries = filtered_df_sidebar.nlargest(5, str(selected_year))[['Country Name', str(selected_year)]].reset_index(drop=True)
bottom_5_countries = filtered_df_sidebar.nsmallest(5, str(selected_year))[['Country Name', str(selected_year)]].reset_index(drop=True)

# Add ranking column
top_5_countries.insert(0, "Rank", range(1, len(top_5_countries) + 1))
bottom_5_countries.insert(0, "Rank", range(1, len(bottom_5_countries) + 1))

# Create two columns for side-by-side tables
col1, col2 = st.columns(2)

# Display top 5 countries in the first column
with col1:
    st.write("**Top 5 Countries:**")
    st.write(top_5_countries.to_html(index=False), unsafe_allow_html=True)

# Display bottom 5 countries in the second column
with col2:
    st.write("**Bottom 5 Countries:**")
    st.write(bottom_5_countries.to_html(index=False), unsafe_allow_html=True)

# Bar Chart: Distribution of Countries by Income Group
st.subheader(f"Country Distribution by Income Group in {selected_year}")

# Group data by IncomeGroup and count the number of countries
income_group_distribution = filtered_df_sidebar.groupby('IncomeGroup')[str(selected_year)].count().reset_index()
income_group_distribution.columns = ['Income Group', 'Number of Countries']

# Plot the bar chart
fig_bar = px.bar(
    income_group_distribution,
    x='Income Group',
    y='Number of Countries',
    title=f"Number of Countries by Income Group ({selected_year})",
    labels={'Number of Countries': 'Number of Countries'},
    color='Income Group',
    text='Number of Countries'  # Display the count on the bars
)
fig_bar.update_layout(showlegend=False, xaxis_title="Income Group", yaxis_title="Number of Countries")

# Display the bar chart
st.plotly_chart(fig_bar, use_container_width=True)

# Line Chart: Compare GDP Trends for Two Countries
st.subheader("Compare GDP Trends for Two Countries")

# Get the list of countries based on the filtered data
filtered_country_list = filtered_df_sidebar['Country Name'].dropna().unique()

# Dropdowns to select two countries based on the filtered list
country_1 = st.selectbox("Select the first country:", filtered_country_list, key="country_1")
country_2 = st.selectbox("Select the second country:", filtered_country_list, key="country_2")

# Filter data for the selected countries
country_1_data = merged_df[merged_df['Country Name'] == country_1]
country_2_data = merged_df[merged_df['Country Name'] == country_2]

# Create a DataFrame for the line chart
if not country_1_data.empty and not country_2_data.empty:
    comparison_df = pd.DataFrame({
        "Year": year_columns,
        country_1: country_1_data.iloc[0][year_columns].values,
        country_2: country_2_data.iloc[0][year_columns].values
    })

    # Plot the line chart
    fig = px.line(
        comparison_df,
        x="Year",
        y=[country_1, country_2],
        labels={"value": "GDP per Capita", "Year": "Year", "variable": "Country"},
        title=f"GDP per Capita Trends: {country_1} vs {country_2}"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please select two valid countries for comparison.")