import streamlit as st
import ParsingModule
import pandas as pd
import numpy as np
import re

import warnings
warnings.filterwarnings("ignore")


# Define the default button color (you can adjust this as desired)
default_color = "#ffa478"
# Define the button CSS styles
button_styles = f"""
    background-color: white;
    color: {default_color};
    border-radius: 20px;
    padding: 10px 20px;
    border: none;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
"""
# Define the button CSS styles when it's clicked
clicked_styles = f"""
    background-color: #ffa478;
    color: white;
"""
st.set_page_config(
    page_title="Experiment types",
    layout="wide",
    page_icon=":construction:",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)

if "template_df" not in st.session_state:
    st.error("No SDRF file was detected. Go to the Home page to select your template.", icon="🚨")  
else:
    template_df = st.session_state["template_df"] 
    with st.container():
        st.write("**This is your current SDRF file.**")
        st.dataframe(template_df)


def update_session_state(df):
    st.session_state["template_df"] = df
st.subheader(":construction: *Under development* :construction:")
st.title("""5. Experiment types""")
st.write(""" :rotating_light:
This application is currently in development and the current page is not yet finalized. We are in touch with several members of the involved communities, 
but we have not yet decided on a strict template. 
If you would like to be a part of this discussion, please use the button in the sidebar to get involved.
""")
url = "https://github.com/bigbio/proteomics-sample-metadata/issues"
button = f'<a href="{url}" style="{button_styles}" id="mybutton" onclick="document.getElementById(\'mybutton\').style.cssText = \'{clicked_styles}\'" target="_blank">Join the community effort</a>'
with st.sidebar:
    st.write(button, unsafe_allow_html=True)


st.write("""Some experiment types have an atypical SDRF structure. Here you can find the community-suggested SDRF columns for such experiments.""")

metaproteomics = st.button('Metaproteomics')
single_cell = st.button('Single cell proteomics')
immunopeptidomics = st.button('Immunopeptidomics')

meta_proteomics_cols = ["characteristics[environmental material]", "characteristics[organism]", "characteristics[diet]", "characteristics[biome]", "characteristics[environmental condition]"]
for button, suggested_cols in zip([metaproteomics], [meta_proteomics_cols]):
    if button:
        col1, col2 = st.columns(2)
        #check which suggested cols are already in the template and which ones are not
        detected_cols = [col for col in suggested_cols if col in template_df.columns]
        cols_to_add = [col for col in suggested_cols if col not in template_df.columns]
        for i in detected_cols:
            with col1:
                st.success(f"The suggested column **{i}** is already in your SDRF file.", icon="✅")
        for i in cols_to_add:
            with col1:
                st.error(f"The suggested column **{i}** is not in your SDRF file. Do you want to add it?", icon="❌")
        with col2:
            st.write("Suggested columns:")
            for c in cols_to_add:
                st.checkbox(f"Add **{c}** to SDRF file", key=c)

