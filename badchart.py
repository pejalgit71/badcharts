import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pydeck as pdk
import matplotlib.pyplot as plt
import os

st.set_page_config(layout="wide")

st.title("📉 Bad vs Good Chart Examples")

# Load default CSV automatically if no upload provided
default_csv_path = "sample_data.csv"
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("CSV loaded successfully!")
elif os.path.exists(default_csv_path):
    df = pd.read_csv(default_csv_path)
    st.info("Using default sample CSV file.")
else:
    st.warning("Please upload a CSV file or provide a 'sample_data.csv' in the app directory.")
    st.stop()

chart_type = st.selectbox("Choose chart type", [
    "Bar Chart", "Pie Chart", "Line Chart", "Map Chart", "Donut Chart"
])

def show_explanations(mistakes):
    with st.expander("❗ 5 Common Mistakes in Bad Chart"):
        for i, (title, reason) in enumerate(mistakes, 1):
            st.markdown(f"**{i}. {title}**: {reason}")

if chart_type == "Bar Chart":
    st.header("1. Bar Chart")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Bad Bar Chart")
        st.bar_chart(df.select_dtypes(include='number').iloc[:, 0])
        show_explanations([
            ("No x-axis labels", "Viewers can't tell what each bar represents."),
            ("Missing title", "Chart purpose is unclear."),
            ("No color distinction", "Can't distinguish between groups/categories."),
            ("Only numeric data shown", "Not meaningful without category labels."),
            ("Overly simplistic", "Lack of customization makes it hard to understand.")
        ])

    with col2:
        st.subheader("✅ Fixed Bar Chart")
        if 'Category' in df.columns and 'Value' in df.columns:
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X("Category", title="Category"),
                y=alt.Y("Value", title="Value"),
                color=alt.Color("Category", legend=None)
            ).properties(
                title="Bar Chart of Values by Category"
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Columns 'Category' and 'Value' required.")

elif chart_type == "Pie Chart":
    st.header("2. Pie Chart")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Bad Pie Chart")
        fig, ax = plt.subplots()
        ax.pie(df.select_dtypes(include='number').iloc[:, 0])
        st.pyplot(fig)
        show_explanations([
            ("No category labels", "Can't tell what each slice represents."),
            ("No values shown", "No idea of proportion."),
            ("Colors too similar", "Hard to differentiate slices."),
            ("No title", "Viewer doesn't know what this pie shows."),
            ("Only values shown", "Without labels, it's meaningless.")
        ])

    with col2:
        st.subheader("✅ Fixed Pie Chart")
        if 'Category' in df.columns and 'Value' in df.columns:
            fig = px.pie(df, names='Category', values='Value', title='Pie Chart of Values')
            st.plotly_chart(fig)
        else:
            st.warning("Columns 'Category' and 'Value' required.")

elif chart_type == "Line Chart":
    st.header("3. Line Chart")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Bad Line Chart")
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.shape[1] >= 2:
            st.line_chart(numeric_df)
        else:
            st.warning("Only one numeric column found; cannot show multiple lines.")

        show_explanations([
            ("Missing x-axis (e.g. time)", "No trend or time pattern shown."),
            ("No category separation", "Lines are not grouped or distinguished."),
            ("No markers or line styles", "Hard to read intersections."),
            ("No axis labels", "Can't interpret values or time scale."),
            ("No title", "Purpose of chart is unclear.")
        ])

    with col2:
        st.subheader("✅ Fixed Line Chart")
        if {'Year', 'Value', 'Category'}.issubset(df.columns):
            try:
                df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
                df = df.dropna(subset=['Year', 'Value'])
                df['Year'] = df['Year'].astype(int)
                df = df.sort_values(by=['Category', 'Year'])
                fig = px.line(
                    df,
                    x='Year',
                    y='Value',
                    color='Category',
                    markers=True,
                    title="Line Chart: Values by Year and Category"
                )
                fig.update_traces(line=dict(width=2))
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Error rendering line chart: {e}")
        else:
            st.warning("Columns 'Year', 'Category', and 'Value' required.")

elif chart_type == "Map Chart":
    st.header("4. Map Chart")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Bad Map Chart")
        if {'Latitude', 'Longitude'}.issubset(df.columns):
            try:
                renamed_df = df.rename(columns={"Latitude": "latitude", "Longitude": "longitude"})
                st.map(renamed_df[['latitude', 'longitude']])
            except Exception as e:
                st.error("Map could not be rendered. Check Latitude and Longitude values.")
        else:
            st.warning("Missing 'Latitude' and 'Longitude' columns for map.")

        show_explanations([
            ("No data labels", "Hard to understand what the locations represent."),
            ("No tooltip/info", "User cannot get insight from points."),
            ("Overlapping points", "Many markers may overlap and be unreadable."),
            ("No zoom/pan control", "Difficult to explore."),
            ("No color coding", "Everything looks the same.")
        ])

    with col2:
        st.subheader("✅ Fixed Map Chart")
        if {'Latitude', 'Longitude'}.issubset(df.columns):
            try:
                # Ensure background map renders by setting API key to None (default open source tiles)
                pdk.settings.mapbox_api_key = None

                midpoint = (df['Latitude'].mean(), df['Longitude'].mean())
                color_by = 'Category' if 'Category' in df.columns else None
                radius_by = 'Value' if 'Value' in df.columns else None

                layer = pdk.Layer(
                    "ScatterplotLayer",
                    data=df,
                    get_position='[Longitude, Latitude]',
                    get_fill_color="[180, 0, 200, 140]",
                    get_radius=30000,
                    pickable=True,
                    auto_highlight=True
                )
                view_state = pdk.ViewState(
                    latitude=midpoint[0],
                    longitude=midpoint[1],
                    zoom=4,
                    pitch=0
                )
                r = pdk.Deck(
                    map_style="road",
                    initial_view_state=view_state,
                    layers=[layer],
                    tooltip={"text": "{Category}: {Value}"} if color_by and radius_by else None
                )
                st.pydeck_chart(r)
            except Exception as e:
                st.error(f"Error rendering map: {e}")
        else:
            st.warning("Missing 'Latitude' and 'Longitude' columns for the improved map.")


elif chart_type == "Donut Chart":
    st.header("5. Donut Chart")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("❌ Bad Donut Chart (Actually Pie)")
        fig = px.pie(df, names='Category', values='Value')
        st.plotly_chart(fig)
        show_explanations([
            ("Not a real donut", "No hole means it's just a pie chart."),
            ("No labels", "Hard to tell what segments represent."),
            ("No values or percentages", "No sense of scale."),
            ("No title", "Viewer doesn’t know context."),
            ("Too many segments", "Hard to compare thin slices.")
        ])

    with col2:
        st.subheader("✅ Fixed Donut Chart")
        if 'Category' in df.columns and 'Value' in df.columns:
            fig = px.pie(df, names='Category', values='Value', hole=0.4,
                         title="Donut Chart of Values by Category")
            st.plotly_chart(fig)
        else:
            st.warning("Columns 'Category' and 'Value' required.")
