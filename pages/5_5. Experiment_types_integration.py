import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import ParsingModule
import common
import re

st.set_page_config(page_title="SDRF Ontology Mapper", layout="wide")
st.title("Experiment types")
st.write("""This page allows you to annotate proposed metadata elements for single cell proteomics, immunopeptidomics and structural proteomics""")
st.write("""These elements are community suggested. To join the discussion on official SDRF-Proteomics go to: https://github.com/bigbio/proteomics-sample-metadata """)

common.inject_sidebar_logo()
with st.sidebar:
    if st.button("Validate SDRF file before download"):
        # Perform validation or conversion
        converted_data = ParsingModule.convert_df(template_df)
        st.success("SDRF file validated! Ready to download.")
        
        st.download_button(
            label="Download validated SDRF file",
            data=converted_data,
            file_name="intermediate_SDRF.sdrf.tsv",
            mime="text/tab-separated-values"
        )

    st.write("""Please refer to your data and lesSDRF within your manuscript as follows:
                 *The experimental metadata has been generated using lesSDRF and is available through ProteomeXchange with the dataset identifier [PXDxxxxxxx]*""")


# ---------------- SESSION STATE CHECK -------------------
if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")  
    st.stop()
else:
    df = st.session_state["template_df"]
    st.write("**This is your current SDRF file:**")
    st.dataframe(df, use_container_width=True)


# ------------------- EXPERIMENT ANNOTATIONS -------------------
EXPERIMENT_ANNOTATIONS = {
    "Structural proteomics": {
        "technology type": {"type": "free_text", "options": ["SDS-gel", "mass photometry", "native MS"]},
        "radiation": {"type": "numeric", "unit": "Gy"}
    },
    "Single-cell proteomics": {
        "Plate number": {"type": "numeric"},
        "XPos": {"type": "text"},
        "YPos": {"type": "text"},
        "Number of cells sampled": {"type": "numeric"},
        "Gradient time": {"type": "time"},
        "LC column used": {"type": "free_text"},
        "Diameter": {"type": "numeric", "unit": "µm"},
        "Elongicity": {"type": "free_text"},
        "Circularity": {"type": "free_text"},
        "Fluorescence": {"type": "boolean"},
        "Intensity": {"type": "numeric"},
        "Humidity (CellenION)": {"type": "numeric", "unit": "%"},
        "Volume (CellenION)": {"type": "numeric", "unit": "pl"},
        "Trypsin concentration (CellenION)": {"type": "numeric"}
    },
    "Immunopeptidomics": {
        "MHC allele": {"type": "ontology"},
        "database": {"type": "free_text"}
    }
}

col1, col2 = st.columns(2)
columns_to_add = []
# --------------- USER SELECT EXPERIMENT --------------------
with col1: 
    st.subheader("1. Select experiment type")
    experiment_type = st.selectbox("Experiment type:", list(EXPERIMENT_ANNOTATIONS.keys()))
    fields = EXPERIMENT_ANNOTATIONS[experiment_type]

# ---------------- USER SELECT COLUMNS ----------------------
with col2:
    st.subheader("2. Select community suggested columns")
    available_columns = list(fields.keys())
    selected_columns = st.multiselect("Columns to add:", available_columns)

st.write("##")

# ---------------- INITIALIZE EDITABLE TABLE -------------------
if selected_columns:
    st.subheader("3. Select if these columns are a sample parameter (characteristic) or a run parameter (comment)")
    
    for col in selected_columns:
        radio_key = f"col_type_{col}"
        if radio_key not in st.session_state:
            st.session_state[radio_key] = "characteristic" #default
        column_type = st.radio(f"Select column type of **{col}**", ["characteristic", "comment"], key=f"col_type_{col}")
        new_col_name = f"{column_type}[{col}]"
        columns_to_add.append(new_col_name)
st.write(columns_to_add)

if st.button("Add column(s) to SDRF"):

    for col in columns_to_add:
        df[col] = ""

builder = GridOptionsBuilder.from_dataframe(df)
builder.configure_grid_options(enableRangeSelection=True, enableFillHandle=True, singleClickEdit=True)

builder.configure_columns(columns_to_add, editable=True,cellEditor="agTextCellEditor",cellStyle={"background-color": "#ffa478"})
st.session_state["template_df"] = df 
    
gridOptions = builder.build()

grid_return = AgGrid(
    df,
    gridOptions=gridOptions,
    update_mode=GridUpdateMode.MANUAL,
    data_return_mode=DataReturnMode.AS_INPUT,
    fit_columns_on_grid_load=False
)
if grid_return["data"] is not None and not grid_return["data"].equals(st.session_state["template_df"]):
    # User clicked update manually
    st.success("✅ SDRF updated")
    df= grid_return["data"]
    st.session_state["template_df"] = df.copy()
    st.rerun()