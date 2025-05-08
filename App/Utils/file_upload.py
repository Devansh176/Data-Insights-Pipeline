import pandas as pd
import json


def get_datatype_input_json(files_dict):
    """
    Process uploaded files and return the required JSON structure, skipping Unnamed columns
    and ensuring integer values are plain integers.
    """
    output_json = {}

    for table_name, df in files_dict.items():

        # Filter out Unnamed columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # Generate the JSON for this table
        table_json = {
            "number_of_rows": len(df),
            "columns": {}
        }

        for column in df.columns:
            column_data = df[column].dropna()  # Drop NaN values to focus on valid data
            if not column_data.empty:
                table_json["columns"][column] = {
                    "unique_count": column_data.nunique(),
                    "value": (
                        column_data.iloc[0].item()
                        if pd.api.types.is_numeric_dtype(column_data)
                        else column_data.iloc[0]
                    ),
                }
            else:
                table_json["columns"][column] = {
                    "unique_count": 0,
                    "value": None,
                }

        # Add this table's JSON to the final output
        output_json[table_name] = table_json

    return output_json


def get_joins_input_json(files_dict, data_type_dict):
    """
    Process uploaded files and dataTypeJson to produce the desired output JSON structure.
    """

    # Initialize the output JSON dictionary
    output_json = {}

    for table_name, df in files_dict.items():

        # Get the table's schema from dataTypeJson
        if table_name not in data_type_dict['tables']:
            continue  # Skip if the table schema is not found in dataTypeJson

        table_schema = data_type_dict['tables'][table_name]
        table_output = {}

        for column, column_properties in table_schema['columns'].items():
            column_data = df[column].dropna()  # Get unique non-NaN values

            column_output = {
                "isIdentifier": column_properties["isIdentifier"],
                "values": [],
                "min_value": None,
                "max_value": None,
            }

            # If the column is an identifier
            if column_properties["isIdentifier"]:
                column_output["values"] = [
                    {
                        "value": value,
                        "occurrence": int(column_data[column_data == value].count())
                    }
                    for value in column_data.unique()[:5]
                ] # Take any 5 unique values

            elif not column_properties["isArray"] and not column_properties["isJson"]:

                # If the column is categorical but not an identifier
                if column_properties["isCategorical"]:
                    column_output["values"] = [
                        {
                            "value": value,
                            "occurrence": int(column_data[column_data == value].count())
                        }
                        for value in column_data.unique()
                    ]

                # Otherwise, take any 5 unique values
                else:
                    column_output["values"] = [
                        {
                            "value": value,
                            "occurrence": int(column_data[column_data == value].count())
                        }
                        for value in column_data.unique()[:5]
                    ]

            # If the column is numerical and not an identifier
            if not column_properties["isIdentifier"] and column_properties["datatype"].lower() in ["float", "double", "integer", "int"]:
                column_output["min_value"] = column_data.min()
                column_output["max_value"] = column_data.max()

            # Add the processed column output to the table output
            table_output[column] = column_output

        # Add the table output to the final output JSON
        output_json[table_name] = table_output

    # Return the output JSON as a dictionary
    return output_json
