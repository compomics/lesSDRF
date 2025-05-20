import streamlit as st
import ParsingModule
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")
from streamlit_tree_select import tree_select
from PIL import Image
import base64
import io
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="SDRF Ontology Mapper", layout="wide")
st.title("SDRF Ontology Mapper")
st.write("""Here you can search for any possible ontology term through the Ontology Lookup Service. It will allow you to use said term as a new column name and fill the values with its child terms or free text""")

import common
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

def update_session_state(df):
    st.session_state["template_df"] = df

if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")  
    st.stop()
else:
    df = st.session_state["template_df"] 
    with st.container():
        st.write("**This is your current SDRF file.**")
        st.dataframe(df)


supported_ontologies = [
    'cl', 'efo', 'hancestro', 'mco', 'ms', 'pride_cv', 'obi',
    'fbbt', 'po', 'clo', 'uberon', 'zfa', 'zfs', 'fbcv',
    'micro', 'panto', 'rs', 'chebi', 'mondo', 'eco', 'mro'
]
@st.cache_data()
def search_ols_term(term, exact=True):
    url = "https://www.ebi.ac.uk/ols4/api/search"
    params = {
        "q": term,
        "type": "class",
        "rows": 100
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    results = response.json()

    if results['response']['numFound'] == 0:
        return []

    seen = set()
    filtered = []
    for doc in results['response']['docs']:
        label = doc.get('label', '').strip().lower()
        obo_id = doc.get('obo_id')
        ontology = doc.get('ontology_name')
        description = doc.get('description')

        if ontology not in supported_ontologies:
            continue

        if exact and label != term.lower():
            continue

        if obo_id and obo_id not in seen:
            seen.add(obo_id)
            filtered.append(doc)

    return filtered

def get_ontology_children(obo_id, ontology):
    term = obo_id.replace(':', '_')
    encoded_url = f"https://www.ebi.ac.uk/ols4/api/ontologies/{ontology}/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F{term}/hierarchicalChildren?lang=en"
    response = requests.get(encoded_url)
    response.raise_for_status()
    data = response.json()
    children = []
    if '_embedded' in data:
        for t in data['_embedded']['terms']:
            children.append({
                'label': t['label'],
                'obo_id': t['obo_id'],
                'description': t['description'] if 'description' in t else ''
            })
    return children

st.header("1. Browse the Ontology Lookup Service (OLS)")
# Step 1: Ontology term search
search_term = st.text_input("1. Search for ontology term", "")
exact_match = st.checkbox("Exact match only", value=True)
if st.button("Search"):
    matches = search_ols_term(search_term, exact=exact_match)
    st.session_state["search_results"] = matches

# Render selectbox if search results are available
if "search_results" in st.session_state and st.session_state["search_results"]:
    matches = st.session_state["search_results"]
    options = [f"{m['label']} ({m['obo_id']}) [{m['ontology_name']}]" for m in matches]
    selected_idx = st.selectbox(
        "2. Select a term from the ontologies", list(range(len(options))), format_func=lambda i: options[i]
    )
    selected = matches[selected_idx]
    st.session_state.selected_term = selected
    st.write("Check if the description matches your intent:", selected)
elif "search_results" in st.session_state:
    st.warning("No matches found.")

# Show child terms of the selected term
if st.session_state.get("selected_term"):
    selected = st.session_state["selected_term"]
    st.subheader("2. Child Terms")
    with st.spinner("Fetching child terms..."):
        children = get_ontology_children(
            obo_id=selected["obo_id"],
            ontology=selected["ontology_name"]
        )

    if children:
        child_df = pd.DataFrame(children)
        st.dataframe(child_df)
    else:
        st.info("No child terms found.")
        child_df = pd.DataFrame()

st.subheader("3. Add this term to SDRF")
col1, col2, col3 = st.columns(3)
with col1:
    add_to_sdrf = st.radio("Do you want to add this term to your SDRF?", ["No", "Yes"], key="add_term")
    if add_to_sdrf == "Yes":
        with col2:
            column_type = st.radio("Select column type", ["characteristic", "comment"], key="col_type")
            column_name = f"{column_type}[{selected['label']}]"
            st.write(f"New column name: **{column_name}**")

            try:
                has_children = not child_df.empty
            except NameError:
                has_children = False

        if has_children:
            with col3:
                fill_method = st.radio("How would you like to fill the new column?", ["Use from child terms", "Enter free text"], key="fill_method")
                if len(child_df) == 1:
                    st.info("Only one child term found — the entire column will be auto-filled with it if selected.")
        else:
            st.info("No child terms found for this ontology term.")
            fill_method = "Enter free text"
    

st.markdown('#')


if st.button("Add column to SDRF"):
    #add column
    df[column_name] = ""
    builder = GridOptionsBuilder.from_dataframe(df)
    builder.configure_grid_options(enableRangeSelection=True, enableFillHandle=True, singleClickEdit=True)
    if fill_method == "Use from child terms":
            builder.configure_columns(
                    column_name,
                    editable=True,
                    cellEditor="agSelectCellEditor",
                    cellEditorParams={"values": child_df['label'].tolist()},
                    cellStyle={"background-color": "#ffa478"}
                )
            st.session_state["template_df"] = df 
            
    else:  # free text
        builder.configure_column(column_name, editable=True,cellEditor="agTextCellEditor",cellStyle={"background-color": "#ffa478"})
        st.session_state["template_df"] = df 
        
    gridOptions = builder.build()

    grid_return = AgGrid(
        df,
        gridOptions=gridOptions,
        update_mode=GridUpdateMode.MANUAL,
        data_return_mode=DataReturnMode.AS_INPUT,
        fit_columns_on_grid_load=False
    )
    if grid_return["data"] is not None and not grid_return["data"].equals(st.session_state.get("template_df")):
        # User clicked update manually
        st.session_state["template_df"] = grid_return["data"]
        
