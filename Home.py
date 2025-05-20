import common
import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import gzip
import json
import ParsingModule
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(
    page_title="Additional columns",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)


common.inject_sidebar_logo()

local_dir = os.path.dirname(__file__)

@st.cache_data
def load_data():
    """Load gzipped JSON data and Unimod CSV"""
    folder_path = os.path.join(local_dir, "data")
    unimod_path = os.path.join(local_dir, "ontology", "unimod.csv")
    data = {}
    for filename in os.listdir(folder_path):
        if re.search(r"archaea|bacteria|eukaryota|virus|unclassified|other sequences", filename):
            continue
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".json.gz"):
            try:
                with gzip.open(file_path, "rb") as f:
                    json_str = f.read().decode('utf-8')
                    try:
                        data[filename.replace(".json.gz", "")] = json.loads(json_str)
                    except json.JSONDecodeError:
                        st.error(f"Error decoding JSON in file {file_path}")
            except gzip.BadGzipFile:
                st.error(f"Error reading {file_path}: not a gzipped file")
        else:
            st.warning(f"Skipping {file_path}: not a gzipped file")

    unimod = pd.read_csv(unimod_path, sep="\t")
    return data, unimod

data_dict, unimod = load_data()

# Store in session state
st.session_state.setdefault("data_dict", data_dict)
st.session_state.setdefault("unimod", unimod)

st.title("Welcome to lesSDRF")
st.subheader("Spending less time on SDRF creates more time for amazing research")

intro_text = """
By providing metadata in a machine-readable format, other researchers can access your data more easily and you maximize its impact. 
The Sample and Data Relationship Format ([SDRF](https://www.nature.com/articles/s41467-021-26111-3)) is the HUPO-PSI recognized metadata format within proteomics. 
lesSDRF will streamline this annotation process for you. This tool is developed by the [CompOmics group](https://compomics.com/) and published in 
[Nature Communications](https://www.nature.com/articles/s41467-023-42543-5).
"""
st.write(intro_text)

instructions_text = """
On this homepage, select the species-specific default SDRF file that matches your study and provide the raw file names. 
Then, follow the steps in the sidebar.  

- Step 1: If you have a local metadata file, you can upload it to map to the SDRF file  
- Step 2: Provide information on potential labels in your sample  
- Step 3: Annotate columns required by SDRF-Proteomics guidelines 
- Step 4: Parse through supported ontologies to find terms matching your research
- Step 5: Community suggested columns for single cell proteomics, immunopeptidomics, structural proteomics etc.

You can download your intermediate file at any given time and return to complete it later.
"""
st.write(instructions_text)

st.markdown("Upload your intermediate SDRF file here:")

upload_df = st.file_uploader(
    "Upload intermediate SDRF file", type=["tsv"], accept_multiple_files=False,
    help='Upload a previously saved SDRF file. It should be in TSV format and not contain more than 500 samples'
)

if upload_df is not None:
    template_df = pd.read_csv(upload_df, sep='\t')
    if template_df.shape[0] > 500:
        st.error('Too many samples, please upload a maximum of 500 samples')
    else:
        builder = GridOptionsBuilder.from_dataframe(template_df)
        builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=500)
        builder.configure_default_column(filterable=True, sortable=True, resizable=True)
        gridOptions = builder.build()
        AgGrid(template_df, gridOptions=gridOptions, height=500, custom_css={"#gridToolBar": {"padding-bottom": "0px !important",}})

        st.session_state["template_df"] = template_df

st.subheader("Start here with a completely new SDRF file")

species = ["", "human", "cell-line", "default", "invertebrates", "plants", "vertebrates"]
selected_species = st.selectbox(
    "Select a species for the SDRF template:",
    species,
    help="This selection impacts the default columns in your SDRF template."
)

if selected_species:
    folder_path = os.path.join(local_dir, "templates")
    template_path = os.path.join(folder_path, f"sdrf-{selected_species}.sdrf.tsv")
    template_df = pd.read_csv(template_path, sep="\t")

    # Add empty columns
    for col in ["comment[modification parameters]", "comment[fragment mass tolerance]", "comment[precursor mass tolerance]"]:
        template_df[col] = np.nan

    uploaded_names = st.text_input(
        "Input raw file names (comma, tab, or space separated):",
        help="Raw file names will populate comment[data file]. Max 2000 files."
    )

    if uploaded_names:
        delimiters = [",", "\t", " "]
        for delim in delimiters:
            if delim in uploaded_names:
                filenames = [name.strip() for name in uploaded_names.split(delim)]
                break
        else:
            filenames = [uploaded_names.strip()]

        if len(filenames) > 2000:
            st.error('Too many samples, please upload a maximum of 2000 samples')
        else:
            template_df["comment[data file]"] = filenames
            st.session_state["template_df"] = template_df
            builder = GridOptionsBuilder.from_dataframe(template_df)
            builder.configure_pagination(paginationAutoPageSize=False, paginationPageSize=500)
            builder.configure_default_column(filterable=True, sortable=True, resizable=True)
            gridOptions = builder.build()
            AgGrid(template_df, gridOptions=gridOptions, height=500, custom_css={"#gridToolBar": {"padding-bottom": "0px !important",}})

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