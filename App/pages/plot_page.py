from Utils import plots
import streamlit as st

params_to_check = ["plot_data", "files", "joins_data"]
missing_params = [param for param in params_to_check if param not in st.session_state]

st.title("Plots")

if missing_params:
    st.error(f"Please Upload files and check back after processing is done!")
else:
    plot_data = st.session_state["plot_data"]
    files_dict = st.session_state["files"]
    joins_data = st.session_state["joins_data"]

    plots.generate_plots(plot_data, files_dict, joins_data)
