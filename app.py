import streamlit as st
import pandas as pd
import altair as alt

# Data Preprocessing
df = pd.read_csv('dog_data.csv')
df = df.drop_duplicates()
df['Breed Group'] = df['Breed Group'].str.replace(" »", "", regex=False)
df['Height'] = df['Height'].str.replace(" inches", "", regex=False)
df['Height'] = df['Height'].str.replace(" (male)", "", regex=False)
df['Height'] = df['Height'].str.replace(" (TOY)", "", regex=False)
df['Weight'] = df['Weight'].str.replace(" (TOY)", "", regex=False)
df['Weight'] = df['Weight'].str.replace(" (male)", "", regex=False)
df['Weight'] = df['Weight'].str.replace(" pounds", "", regex=False)
df['Life Expectancy'] = df['Life Expectancy'].str.replace(" years", "", regex=False)

# Extract averages from ranges
def extract_avg(range_str):
    if isinstance(range_str, str):
        try:
            range_str = range_str.replace(' ', '')
            low, high = range_str.split('-')
            return (float(low) + float(high)) / 2
        except ValueError:
            return None
    return None

df['Height'] = df['Height'].apply(extract_avg)
df['Weight'] = df['Weight'].apply(extract_avg)
df['Life Expectancy'] = df['Life Expectancy'].apply(extract_avg)

# Convert columns to numeric
df['Height'] = pd.to_numeric(df['Height'], errors='coerce')
df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce')
df['Life Expectancy'] = pd.to_numeric(df['Life Expectancy'], errors='coerce')

# Streamlit App
st.title("Dog Breed Insights")
st.sidebar.title("Filters")

# Sidebar Filters
breed_group = st.sidebar.selectbox("Select Breed Group", options=["All"] + df["Breed Group"].unique().tolist())
height_range = st.sidebar.slider("Height Range", int(df["Height"].min()), int(df["Height"].max()), (int(df["Height"].min()), int(df["Height"].max())))
weight_range = st.sidebar.slider("Weight Range", int(df["Weight"].min()), int(df["Weight"].max()), (int(df["Weight"].min()), int(df["Weight"].max())))
life_expectancy_range = st.sidebar.slider("Life Expectancy Range", int(df["Life Expectancy"].min()), int(df["Life Expectancy"].max()), (int(df["Life Expectancy"].min()), int(df["Life Expectancy"].max())))
selected_breeds = st.sidebar.multiselect("Select Specific Breeds", options=df["Breed"].unique())

# Apply Filters
filtered_df = df[
    (df["Height"] >= height_range[0]) & (df["Height"] <= height_range[1]) &
    (df["Weight"] >= weight_range[0]) & (df["Weight"] <= weight_range[1]) &
    (df["Life Expectancy"] >= life_expectancy_range[0]) & (df["Life Expectancy"] <= life_expectancy_range[1])
]
if breed_group != "All":
    filtered_df = filtered_df[filtered_df["Breed Group"] == breed_group]
if selected_breeds:
    filtered_df = filtered_df[filtered_df["Breed"].isin(selected_breeds)]

# Tabs
tab1, tab2, tab3 = st.tabs(["Dataset Overview", "Visualizations", "Comparative Analysis"])

# Tab 1: Dataset Overview
with tab1:
    st.subheader("Filtered Dataset")
    st.dataframe(filtered_df)
    st.download_button("Download Data", filtered_df.to_csv(index=False), "filtered_data.csv")

# Tab 2: Visualizations
with tab2:
    st.subheader("Exploratory Data Analysis")

    # Box Plot: Life Expectancy by Breed Group
    box_plot = alt.Chart(filtered_df).mark_boxplot().encode(
        x=alt.X("Breed Group:N", title="Breed Group"),
        y=alt.Y("Life Expectancy:Q", title="Life Expectancy (Years)", scale=alt.Scale(domain=[8, 18])),
        color="Breed Group:N"
    )
    st.altair_chart(box_plot, use_container_width=True)


    # Scatterplot: Height vs Life Expectancy with Regression Line
    height_vs_life = alt.Chart(filtered_df).mark_point().encode(
        x=alt.X("Height:Q", title="Height (inches)", scale=alt.Scale(domain=[5, 35])),
        y=alt.Y("Life Expectancy:Q", title="Life Expectancy (Years)", scale=alt.Scale(domain=[5, 20])),
        color="Breed Group:N",
        tooltip=["Breed", "Height", "Life Expectancy"]
    ).interactive()
    height_reg_line = height_vs_life.transform_regression(
        "Height", "Life Expectancy"
    ).mark_line(color="red")
    st.altair_chart(height_vs_life + height_reg_line, use_container_width=True)

    # Scatterplot: Weight vs Life Expectancy with Regression Line
    weight_vs_life = alt.Chart(filtered_df).mark_point().encode(
        x=alt.X("Weight:Q", title="Weight (pounds)", scale=alt.Scale(domain=[5, 200])),
        y=alt.Y("Life Expectancy:Q", title="Life Expectancy (Years)", scale=alt.Scale(domain=[5, 20])),
        color="Breed Group:N",
        tooltip=["Breed", "Weight", "Life Expectancy"]
    ).interactive()
    weight_reg_line = weight_vs_life.transform_regression(
        "Weight", "Life Expectancy"
    ).mark_line(color="blue")
    st.altair_chart(weight_vs_life + weight_reg_line, use_container_width=True)


# Tab 3: Comparative Analysis
with tab3:
    st.subheader("Breed Comparison")
    breeds_to_compare = st.multiselect("Select Two Breeds to Compare", options=df["Breed"].unique(), default=df["Breed"].unique()[:2])
    if len(breeds_to_compare) == 2:
        breed_data = df[df["Breed"].isin(breeds_to_compare)]
        st.write(breed_data)

# Summary
st.sidebar.header("Summary")
st.sidebar.write(f"Total Breeds: {len(df)}")
st.sidebar.write(f"Filtered Breeds: {len(filtered_df)}")
