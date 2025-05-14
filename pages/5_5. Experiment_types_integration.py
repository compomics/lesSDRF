import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import ParsingModule
import common

st.set_page_config(page_title="SDRF Ontology Mapper", layout="wide")
st.title("Experiment types")
st.write("""This page allows you to annotate proposed metadata elements for single cell proteomics, immunopeptidomics and structural proteomics""")
st.write("""These elements are community suggested. To join the discussion on official SDRF-Proteomics go to: https://github.com/bigbio/proteomics-sample-metadata """)

common.inject_sidebar_logo()

# ---------------- SESSION STATE CHECK -------------------
if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")  
    st.stop()
else:
    template_df = st.session_state["template_df"]

st.write("**This is your current SDRF file:**")
st.dataframe(template_df, use_container_width=True)

# ------------------- EXPERIMENT ANNOTATIONS -------------------
EXPERIMENT_ANNOTATIONS = {
    "Structural proteomics": {
        "technology type": {"type": "free_text", "options": ["SDS-gel", "mass photometry", "native MS"]},
        "radiation": {"type": "numeric", "unit": "Gy"}
    },
    "SCP": {
        "Plate (batch)": {"type": "numeric"},
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

# --------------- USER SELECT EXPERIMENT --------------------
st.subheader("Select experiment type")
experiment_type = st.selectbox("Experiment type:", list(EXPERIMENT_ANNOTATIONS.keys()))
fields = EXPERIMENT_ANNOTATIONS[experiment_type]

# ---------------- USER SELECT COLUMNS ----------------------
st.subheader("Select columns to annotate")
available_columns = list(fields.keys())
selected_columns = st.multiselect("Columns to add:", available_columns)

# ---------------- INITIALIZE EDITABLE TABLE -------------------
if selected_columns:
    # Create a working DataFrame with one row per sample
    mapping_table = pd.DataFrame({ "File name": template_df["comment[data file]"].unique() })
    
    # Add selected columns
    for col in selected_columns:
        mapping_table[col] = ""  # init empty

    # --------------- CONFIGURE AGGRID -------------------
    builder = GridOptionsBuilder.from_dataframe(mapping_table)
    for col in mapping_table.columns:
        if col == "File name":
            builder.configure_column(col, editable=False)
        else:
            col_def = fields[col]
            if "options" in col_def:
                builder.configure_column(
                    col,
                    editable=True,
                    cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": [""] + col_def["options"]}
                )
            else:
                builder.configure_column(col, editable=True, cellEditor="agTextCellEditor")
    builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=50)
    builder.configure_grid_options(enableRangeSelection=True, enableFillHandle=True, pagination=True)

    gridOptions = builder.build()

    grid_return = AgGrid(
        mapping_table,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MANUAL,
        data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=True,
        height=400
    )

    updated_table = grid_return["data"]

    # ---------------- SAVE ANNOTATIONS -------------------
    if st.button("Save annotations to SDRF"):
        for col in selected_columns:
            values = updated_table[col].values
            if col not in template_df.columns:
                template_df[col] = np.nan
            # propagate values by matching file names
            for i, file in enumerate(updated_table["File name"]):
                template_df.loc[template_df["comment[data file]"] == file, col] = values[i]
        st.session_state["template_df"] = template_df
        st.success("Annotations saved to SDRF!")
        st.write(template_df)

else:
    st.info("✅ Select columns to annotate to proceed.")
