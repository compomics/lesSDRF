import streamlit as st
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
import re
import ParsingModule
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from streamlit_tree_select import tree_select
from collections import defaultdict

st.set_page_config(
    page_title="Labeling",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)
st.title("2. Labeling")
st.markdown(
    """If a raw file contains multiple labels, every label will need to be annotated on a different row. Here you can map label information to your raw files. 
    As a result, the raw file information will be duplicated with the correct label filled in"""
)

data_dict = st.session_state["data_dict"]
# Get filled in template_df from other page
# if template_df is not in the session state, don't run all the code below
if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")  
    st.stop()
else:
    template_df = st.session_state["template_df"] 
    st.write("**This is your current SDRF file.**")
    st.write(template_df)

if "all_selected_labels" not in st.session_state:
    st.session_state["all_selected_labels"] = []

with st.sidebar:
    download = st.download_button("Press to download SDRF file",ParsingModule.convert_df(template_df), "intermediate_SDRF.sdrf.tsv", help="download your SDRF file")
    
#first select the labels
st.write("Input the label that was used in your experiment. If no label was added, indicate this using *label free sample*.")
all_label_elements = data_dict["all_label_elements"]
label_nodes = data_dict["label_nodes"]
with st.form("Select here your ontology terms using the autocomplete function or the ontology-based tree menu", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        # selectbox with search option
        all_label_elements.append(" ")
        all_label_elements = set(all_label_elements)
        return_search = st.multiselect(
            "Select your matching ontology term using this autocomplete function",
            all_label_elements)
    with col2:
        st.write("Or follow the ontology based drop down menu below")
        return_select = tree_select(label_nodes, no_cascade=True, expand_on_click=True, check_model="leaf")
    all_selected_labels = return_search + return_select["checked"]
    all_selected_labels = [i.split(',')[-1] for i in all_selected_labels if i is not None]
    s = st.form_submit_button("Submit selection")
    if s:
        st.write(f"Selection contains: {all_selected_labels}")
        st.session_state["all_selected_labels"] = all_selected_labels
#match filenames to labels
st.write("Match the filenames to the labels you selected above. Select ALL if the label is found in all raw files.")
label_dict = defaultdict(list)
for label in all_selected_labels:
    selected_files = st.multiselect(f"Select files labeled with {label}.", ["ALL"] + template_df["comment[data file]"].values.tolist(), key=f"selected_label_{label}")
    for i in selected_files:
        label_dict[i].append(label)
ready = st.checkbox('Ready?')
# based on the label_dict, duplicate rows with comment[data file] in the keys of the lable_dict
# duplicate the row with each row having one of the labels in the characteristics[label] column that is in the value of the label_dict
# if the key is ALL, duplicate the row for each label from the all_selected_labels list

if ready:
    #first get the rows that need to be duplicated
    new_rows = []
    all_selected_labels = st.session_state["all_selected_labels"]
    for filename, label_list in label_dict.items():
        if filename == "ALL":
            rows_to_add = template_df.copy()
        else:
            rows_to_add = template_df[template_df["comment[data file]"] == filename]
        label_idx = 0
        n = len(label_list)
        for i in range(n):
            new_row = rows_to_add.copy()
            new_row["comment[label]"] = label_list[label_idx]
            label_idx += 1
            new_rows.append(new_row)
    template_df = pd.concat(new_rows, ignore_index=True)
    template_df = template_df.sort_values(by='comment[data file]')
    st.write("SDRF file with label information")
    st.dataframe(template_df)
    st.session_state["template_df"] = template_df