import streamlit as st

params_to_check = ["metadata", "joins_data"]
missing_params = [param for param in params_to_check if param not in st.session_state]

st.title("Metadata")

if missing_params:
    st.error(f"Please Upload files and check back after processing is done!")
else:
    st.write(st.session_state["joins_data"]["description"])

    st.json(st.session_state["metadata"])
