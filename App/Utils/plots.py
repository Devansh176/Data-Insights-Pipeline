import pandas as pd
import plotly.express as px
import streamlit as st


def generate_plots2(input_json, files_dict, joinsjson):
    """
    Generates Plotly plots based on input JSON and displays them in Streamlit.
    """
    joins = joinsjson.get("joins", [])

    for plot_config in input_json:
        # Extract plot configuration
        table_1 = plot_config["table_1"]
        table_2 = plot_config["table_2"]
        column_1 = (
            plot_config["column_1"]
            if plot_config["value_column_1"] is None
            else plot_config["value_column_1"]
        )
        column_2 = (
            plot_config["column_2"]
            if plot_config["value_column_2"] is None
            else plot_config["value_column_2"]
        )
        plot_type = plot_config["plot_type"]
        business_insight = plot_config["business_insight"]

        # Load dataframes
        df1 = files_dict[table_1]
        if table_1 == table_2:
            df2 = df1  # Same table case
        else:
            df2 = files_dict[table_2]
            # Join the tables if they are different
            join_info = next(
                (
                    j
                    for j in joins
                    if j["table_1"] == table_1 and j["table_2"] == table_2
                ),
                None,
            )
            if join_info is not None:
                df1 = df1.merge(
                    df2,
                    left_on=join_info["column_1"],
                    right_on=join_info["column_2"],
                    suffixes=("_table1", "_table2"),
                )

        # Generate plots based on plot type
        fig = None

        if plot_type == "line":
            fig = px.line(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "scatter":
            fig = px.scatter(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "bar":
            fig = px.bar(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "box":
            fig = px.box(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "violin":
            fig = px.violin(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "heatmap":
            fig = px.density_heatmap(
                df1, x=column_1, y=column_2, title=business_insight
            )
        elif plot_type == "histogram":
            fig = px.histogram(df1, x=column_1, y=column_2, title=business_insight)
        elif plot_type == "density_contour":
            fig = px.density_contour(
                df1, x=column_1, y=column_2, title=business_insight
            )
        elif plot_type == "pie":
            if column_2:  # Use column_2 for values if available
                fig = px.pie(
                    df1,
                    names=column_1,
                    values=column_2,
                    title=business_insight,
                )
            else:  # Default to counts for column_1
                fig = px.pie(
                    df1,
                    names=column_1,
                    title=business_insight,
                )
        elif plot_type == "bubble":
            # Bubble chart as a scatter plot with size argument
            fig = px.scatter(
                df1,
                x=column_1,
                y=column_2,
                size=plot_config.get("bubble_size_column"),
                title=business_insight,
            )
        else:
            st.write(f"Unsupported plot type: {plot_type}")
            continue

        # Display plot in Streamlit
        if fig is not None:
            st.subheader(business_insight)
            st.plotly_chart(fig)


def generate_plots(input_json, files_dict, joinsjson):
    """
    Generates Plotly plots based on input JSON and displays them in Streamlit.
    """
    joins = joinsjson.get("joins", [])

    for plot_config in input_json:
        try:
            # Extract plot configuration
            table_1 = plot_config["table_1"]
            table_2 = plot_config["table_2"]
            column_1 = (
                plot_config["column_1"]
                if plot_config["value_column_1"] is None
                else plot_config["value_column_1"]
            )
            column_2 = (
                plot_config["column_2"]
                if plot_config["value_column_2"] is None
                else plot_config["value_column_2"]
            )
            plot_type = plot_config["plot_type"]
            business_insight = plot_config["business_insight"]

            # Load dataframes
            df1 = files_dict[table_1]
            if table_1 == table_2:
                df2 = df1  # Same table case
            else:
                df2 = files_dict[table_2]
                # Join the tables if they are different
                join_info = next(
                    (
                        j
                        for j in joins
                        if j["table_1"] == table_1 and j["table_2"] == table_2
                    ),
                    None,
                )
                if join_info is not None:
                    df1 = df1.merge(
                        df2,
                        left_on=join_info["column_1"],
                        right_on=join_info["column_2"],
                        suffixes=("_table1", "_table2"),
                    )

            # Resolve column names with suffixes if necessary
            resolved_column_1 = resolve_column_name(column_1, df1)
            resolved_column_2 = resolve_column_name(column_2, df1)

            if resolved_column_1 is None or resolved_column_2 is None:
                st.error(
                    f"Columns {column_1} or {column_2} not found in DataFrame after join."
                )
                continue

            # Generate plots based on plot type
            fig = None
            if plot_type == "line":
                fig = px.line(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "scatter":
                fig = px.scatter(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "bar":
                fig = px.bar(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "box":
                fig = px.box(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "violin":
                fig = px.violin(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "heatmap":
                fig = px.density_heatmap(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "histogram":
                fig = px.histogram(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "density_contour":
                fig = px.density_contour(
                    df1, x=resolved_column_1, y=resolved_column_2, title=business_insight
                )
            elif plot_type == "pie":
                if resolved_column_2:  # Use column_2 for values if available
                    fig = px.pie(
                        df1,
                        names=resolved_column_1,
                        values=resolved_column_2,
                        title=business_insight,
                    )
                else:  # Default to counts for column_1
                    fig = px.pie(
                        df1,
                        names=resolved_column_1,
                        title=business_insight,
                    )
            elif plot_type == "bubble":
                fig = px.scatter(
                    df1,
                    x=resolved_column_1,
                    y=resolved_column_2,
                    size=plot_config.get("bubble_size_column"),
                    title=business_insight,
                )
            else:
                st.write(f"Unsupported plot type: {plot_type}")
                continue

            # Display plot in Streamlit
            if fig is not None:
                st.subheader(business_insight)
                st.plotly_chart(fig)
        except:
            continue


def resolve_column_name(column_name, dataframe):
    """
    Resolves the correct column name in a DataFrame by checking for suffixes.
    """
    if column_name in dataframe.columns:
        return column_name
    # Check for column name with '_table1' or '_table2' suffixes
    if f"{column_name}_table1" in dataframe.columns:
        return f"{column_name}_table1"
    if f"{column_name}_table2" in dataframe.columns:
        return f"{column_name}_table2"
    return None  # Column not found
