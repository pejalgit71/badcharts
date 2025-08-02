import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import pydeck as pdk
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("📉 Bad vs Good Chart Examples")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("CSV loaded successfully!")

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
                    color=alt.value("steelblue")
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
            st.line_chart(df.select_dtypes(include='number').iloc[:, 0])
            show_explanations([
                ("Missing x-axis (e.g. time)", "No trend or time pattern shown."),
                ("No category separation", "Lines are not grouped or distinguished."),
                ("No markers or line styles", "Hard to read intersections."),
                ("No axis labels", "Can't interpret values or time scale."),
                ("No title", "Purpose of chart is unclear.")
            ])

        with col2:
            st.subheader("✅ Fixed Line Chart")
            if 'Year' in df.columns and 'Value' in df.columns and 'Category' in df.columns:
                fig = px.line(df, x="Year", y="Value", color="Category", markers=True,
                              title="Line Chart: Values by Year and Category")
                st.plotly_chart(fig)
            else:
                st.warning("Columns 'Year', 'Category', and 'Value' required.")

    elif chart_type == "Map Chart":
        st.header("4. Map Chart")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("❌ Bad Map Chart")
            st.map(df)
            show_explanations([
                ("No data labels", "Hard to understand what the locations represent."),
                ("No tooltip/info", "User cannot get insight from points."),
                ("Overlapping points", "Many markers may overlap and be unreadable."),
                ("No zoom/pan control", "Difficult to explore."),
                ("No color coding", "Everything looks the same.")
            ])

        with col2:
            st.subheader("✅ Fixed Map Chart")
            if 'Latitude' in df.columns and 'Longitude' in df.columns:
                layer = pdk.Layer(
                    'ScatterplotLayer',
                    data=df,
                    get_position='[Longitude, Latitude]',
                    get_radius=50000,
                    get_fill_color='[180, 0, 200, 140]',
                    pickable=True
                )

                view_state = pdk.ViewState(
                    latitude=4.2105,
                    longitude=101.9758,
                    zoom=5,
                    pitch=0
                )

                st.pydeck_chart(pdk.Deck(
                    map_style='mapbox://styles/mapbox/light-v9',
                    layers=[layer],
                    initial_view_state=view_state,
                    tooltip={"text": "{Category}: {Value}"}
                ))
            else:
                st.warning("Columns 'Latitude' and 'Longitude' required.")

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

else:
    st.info("Please upload a CSV file to begin.")
