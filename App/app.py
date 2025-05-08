import streamlit as st
from Utils import file_upload, api, data_profiling, aws_store, plots
import json
import pandas as pd

# Title for the app
st.title("PipelineX - Team SAAS")

# Description or instructions
st.write("Upload your files here for processing!")

# File uploader (allow multiple file uploads)
uploaded_files = st.file_uploader(
    "Choose files", type=["csv", "xlsx", "json"], accept_multiple_files=True
)


# Handle uploaded files
if uploaded_files and st.button("Process Data"):

    files_dict = {}

    for file in uploaded_files:
        # Read the file into a Pandas DataFrame based on file type
        if file.type == "text/csv":
            df = pd.read_csv(file)
        elif (
            file.type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            df = pd.read_excel(file)
        elif file.type == "application/json":
            df = pd.read_json(file)
        else:
            continue  # Skip unsupported file types

        # Extract table name from the file name (without extension)
        table_name = file.name.split(".")[0]

        files_dict[table_name] = df

    tasks_list = [
        "Task 1: Getting Datatypes",
        "Task 2: Expanding Object Values to Columns and Updating Info",
        "Task 3: Identifying Table Joins and Getting Outlier Info",
        "Task 4: Getting Plotting Information",
        "Task 5: Generating Metadata",
        "Task 6: Storing Metadata in RDS",
        "Task 7: Final data Cleaning",
        "Task 8: Uploading transformed data to S3",
    ]

    done_processing = False
    # --------------------------------------------------------------------------------------------------------

    # Process the files to generate JSON
    st.write(f"🔄 **{tasks_list[0]} ...**")
    with st.spinner("Working on Task 1..."):
        result_json = file_upload.get_datatype_input_json(files_dict)
        datatypesResponse = api.getDataTypes(result_json)
        dataTypeJson = json.loads(datatypesResponse.strip("```json").strip("```"))
    st.success(f"✅ Task 1 Completed")

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[1]} ...**")
    with st.spinner("Working on Task 2..."):
        newColumnAdded = data_profiling.expandObjectValuesToColumns(
            files_dict, dataTypeJson
        )
        if newColumnAdded:
            # Process the files to generate JSON
            result_json = file_upload.get_datatype_input_json(files_dict)

            datatypesResponse = api.getDataTypes(result_json)
            dataTypeJson = json.loads(datatypesResponse.strip("```json").strip("```"))
    st.success(f"✅ Task 2 Completed")

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[2]} ...**")
    with st.spinner("Working on Task 3..."):
        joinsInputJson = file_upload.get_joins_input_json(files_dict, dataTypeJson)
        joinsResponse = api.getJoins(joinsInputJson)
        joinJson = json.loads(joinsResponse.strip("```json").strip("```"))
    st.success(f"✅ Task 3 Completed")

    st.session_state["joins_data"] = joinJson

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[3]} ...**")
    with st.spinner("Working on Task 4..."):
        plotResponse = api.getPlots(dataTypeJson, joinJson)
        plotJson = json.loads(plotResponse.strip("```json").strip("```"))
    st.success(f"✅ Task 4 Completed")

    st.session_state["plot_data"] = plotJson
    st.session_state["files"] = files_dict

    # --------------------------------------------------------------------------------------------------------

    # plots.generate_plots(plotJson, files_dict, joinJson)

    st.write(f"🔄 **{tasks_list[4]} ...**")
    with st.spinner("Working on Task 5..."):
        metadata = data_profiling.createMetadata(
            dataTypeJson, joinJson, files_dict, uploaded_files
        )
    st.success(f"✅ Task 5 Completed")

    st.session_state["metadata"] = metadata

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[5]} ...**")
    with st.spinner("Working on Task 6..."):
        metadataTable = aws_store.storeMetadataOnRDS(metadata)
    st.success(f"✅ Task 6 Completed")

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[6]} ...**")
    with st.spinner("Working on Task 7..."):
        data_profiling.cleanData(dataTypeJson, files_dict)
    st.success(f"✅ Task 7 Completed")

    # --------------------------------------------------------------------------------------------------------

    st.write(f"🔄 **{tasks_list[7]} ...**")
    with st.spinner("Working on Task 8..."):
        fileNames = []

        for tableName, df in files_dict.items():
            df.to_csv("/tmp/" + tableName + "-transformed.csv", index=False)
            fileNames.append(tableName + "-transformed.csv")

        aws_store.putFilesToS3(fileNames)
    st.success(f"✅ Task 8 Completed")

    # --------------------------------------------------------------------------------------------------------
    st.balloons()
    done_processing = True

    if done_processing and st.download_button(
        label="Download S3 Files",
        data=aws_store.downloadFilesFromS3(),
        file_name="s3_files.zip",
        mime="application/zip",
    ):
        st.success("✅ Your files have been processed and downloaded!")

    if done_processing:
        st.page_link("pages/plot_page.py")
        st.page_link("pages/metadata_page.py")

elif not uploaded_files:
    st.warning("⚠️ Please Upload at least one file for processing.")
