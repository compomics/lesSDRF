import streamlit as st
import pandas as pd
import re
import numpy as np

import ParsingModule
import warnings
warnings.filterwarnings("ignore")
import os
import json
import gzip
local_dir = os.path.dirname(__file__)
    
st.set_page_config(
    page_title="SDRF annotation tool",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)

#get local directory using os, and add the data folder to the path



# use streamlit cache data to load gzipped jsons files from folder
@st.cache_data
def load_data():
    local_dir = os.path.dirname(__file__)
    folder_path = os.path.join(local_dir, "data")
    unimod_path = os.path.join(local_dir, "ontology", "unimod.csv")
    data = {}
    for filename in os.listdir(folder_path):
        # do not load the files containing the following names: archae, bacteria, eukaryota, virus, unclassified, other sequences
        if re.search(r"archaea|bacteria|eukaryota|virus|unclassified|other sequences", filename):
            continue
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".json.gz"):
            try:
                with gzip.open(file_path, "rb") as f:
                    file_data = json.load(f)
                    filename_key = filename.replace(".json.gz", "")
                    data[filename_key] = file_data
            except gzip.BadGzipFile:
                st.write(f"Error reading file {file_path}: not a gzipped file")
        else:
            st.write(f"Skipping file {file_path}: not a gzipped file")

    unimod = pd.read_csv(unimod_path, sep="\t")
    return data, unimod


data_dict, unimod = load_data()
if data_dict:
    st.success(f"*Data was loaded*", icon="✅")
else:
    st.error("Failed loading data", icon="❌")
if "data_dict" not in st.session_state:
    st.session_state["data_dict"] = data_dict
if "unimod" not in st.session_state:
    st.session_state["unimod"] = unimod


st.title("Welcome to lesSDRF :wave:")
st.subheader("The SDRF annotation tool, because less is more")
st.markdown(
    """The Sample and Data Relationship Format (SDRF) is a crucial tool for maximizing the potential impact of your data. 
    By making metadata available and machine-readable, other researchers can study your data more easily."""
)
st.markdown(
    """ This tool will help you to annotate your data with the correct metadata in several steps for a maximum of 250 samples.
    First, on this homepage, you will need to select a default SDRF file based on the species of your sample and provide the raw file names. 
    Then you can follow the steps in the sidebar.  
- Step 1: If you have a local metadata file, you can upload it to map to the SDRF file
- Step 2: Provide information on potential labels in your sample
- Step 3: Fill in the columns that are required for a valid SDRF
- Step 4: Fill in columns with additional information to further optimise your SDRF file  
- Step 5: For atypical experiment types, you can check community suggested columns \n
"""
)

st.markdown("""You are able to download the intermediate file at any given timepoint, so you can come back to the other steps whenever is suitable for you.  
If this is the case right now, please upload your intermediate SDRF file here:""")

upload_df = st.file_uploader(
    "Upload intermediate SDRF file", type=["tsv"], accept_multiple_files=False, help='Upload a previously saved SDRF file. It should be in tsv format and should not contain more than 250 samples'
)
if upload_df is not None:
    template_df = pd.read_csv(upload_df, sep='\t')
    if template_df.shape[0]>250:
        st.error('Too many samples, please upload a maximum of 250 samples')
    else:
        st.write(template_df)
        st.session_state["template_df"] = template_df

st.markdown("""In need of some inspiration? Download this example SDRF file to get an idea of the required output""")
with open(f'{local_dir}/example_SDRF.tsv', 'rb') as f:
    st.download_button("Download example SDRF", f, file_name="example.sdrf.tsv")


st.header("If you're starting from scratch, start here")
st.subheader("Select your species")
species = ["","human", "cell-line", "default", "nonvertebrates", "plants", "vertebrates"]
selected_species = st.selectbox("""Select a species for the SDRF template which will contain the basic colummns to fill in for this specific species. 
If your species is not in the drop down list, you can always use the default template.""", 
species, help="This species selection will impact the default columns present in your SDRF template. You can always add more columns in step *Additional columns*.")

if selected_species != "":
    folder_path = os.path.join(local_dir, "templates")
    # Load the corresponding CSV file based on the selected species
    template_df = pd.read_csv(
        f"{folder_path}/sdrf-{selected_species}.tsv",
        sep="\t",
    )
    template_df["comment[modification parameters]"] = np.nan
    template_df["comment[fragment mass tolerance]"] = np.nan
    template_df["comment[precursor mass tolerance]"] = np.nan

    # Ask user to upload filenames of their samples
    filenames = []
    uploaded_names = st.text_input("Input raw file names as a comma separated list", help="The raw file names will be input in the comment[data file] column and are the basis of your SDRF file. Input maximum 250 raw files")
    if uploaded_names is not None:
        uploaded_names = re.sub(" ", "", uploaded_names)
        uploaded_names = uploaded_names.split(",")
        filenames.append(uploaded_names)
    if len(filenames[0]) > 250:
        st.error('Too many samples, please upload a maximum of 250 samples')
    else:
        st.write(f"Added filenames: {filenames[0]}")
        ## Store filenames in the dataframe
        template_df["comment[data file]"] = filenames[0]
        st.session_state["template_df"] = template_df

    ## Show the data in a table
    st.write(template_df)
    if "template_df" not in st.session_state:
        st.session_state["template_df"] = template_df
    with st.sidebar:
        download = st.download_button("Press to download SDRF file",ParsingModule.convert_df(template_df), "intermediate_SDRF.sdrf.tsv", help="download your SDRF file")
