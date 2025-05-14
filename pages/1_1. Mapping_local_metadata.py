import common
import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import gzip
import json
import ParsingModule

    
st.set_page_config(
    page_title="Map local metadata",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)

common.inject_sidebar_logo()
local_dir = os.path.dirname(__file__)

# --- constants ---


TEMPLATE_COLUMNS = ["source name", "assay name", "technology type", "characteristics[age]",
    "characteristics[ancestry category]",
    "characteristics[biological replicate]",
    "characteristics[cell line]",
    "characteristics[cell type]",
    "characteristics[developmental stage]",
    "characteristics[disease]",
    "characteristics[individual]",
    "characteristics[organism part]",
    "characteristics[organism]",
    "characteristics[sex]",
    "characteristics[enrichment process",
    "characteristics[compound]",
    "characteristics[concentration of compound]",
    "comment[modification parameters]",
    "comment[cleavage agent details]",
    "comment[data file]",
    "comment[fraction identifier]",
    "comment[fractionation method]",
    "comment[instrument]",
    "comment[label]",
    "comment[technical replicate]",
    "comment[fragment mass tolerance]",
    "comment[precursor mass tolerance]",
    "comment[dissociation method]",
    "characteristics[spiked compound]",
    "characteristics[synthetic peptide]",
    "characteristics[phenotype]",
    "comment[depletion]"]
VALUE_COLUMNS=["source name", "assay name", "comment[data file]","comment[fraction identifier]","comment[technical replicate]"]
OTHER_COLUMNS = ["characteristics[sex]", "characteristics[age]"]
MAP_ORGANISM_DICT = {'Homo sapiens': ['Human', 'human', 'homo sapiens', 'Homo Sapiens'], 
                                'Mus musculus': ['mouse', 'Mouse', 'Mus Musculus', 'mus musculus'],
                                'Arabidopsis thaliana': ['arabidopsis thaliana', 'Arabidopsis Thaliana', 'arabidopsis', 'Arabidopsis', 'thale cress'], 
                                'Drosophila melanogaster': ['drosophila', 'Drosophila', 'Drosophila Melanogsaster', 'drosophila melanogaster', 'fruitfly', 'fruit fly'],
                                'Saccharomyces cerevisiae':['Saccharomyces Cerevisiae', 'saccharomyces cerevisiae', "brewer's yeast", "Brewer's yeast"],
                                'Caenorhabditis elegans':['C. Elegans', 'C. elegans', 'c. elegans', 'caenorhabditis elegans', 'Caenorhabditis Elegans', 'worm', 'Worm'],
                                'Danio rerio':['Danio Rerio', 'danio rerio', 'zebrafish', 'Zebrafish'],
                                'Escherichia coli': ['E. Coli', 'E. coli', 'e. coli', 'Escherichia Coli', 'escherichia coli']}

# --- helpers ---
def validate_sex_column(values):
    return all(x in ['M', 'F', 'NA'] for x in values)

def map_organism(values):
    for key, synonyms in MAP_ORGANISM_DICT.items():
        values = [key if v in synonyms else v for v in values]
    return values

def check_ontology(values, ontology_terms):
    return set(values).issubset(set(ontology_terms))

def normalize_organism(values):
    """Replace synonyms in values with canonical organism names."""
    normalized = []
    for val in values:
        replaced = False
        for canonical, synonyms in MAP_ORGANISM_DICT.items():
            if val in synonyms:
                normalized.append(canonical)
                replaced = True
                break
        if not replaced:
            normalized.append(val)
    return normalized
 # --- main UI ---   
st.title("1. Map local metadata to SDRF")
st.markdown("""
If you have a local metadata file available, you can map the data to the required SDRF columns.
**Important:** upload a CSV, TSV, or XLSX. Order of raw file names should match those from the previous step.
""")

if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")
    st.stop()

template_df = st.session_state["template_df"]
data_dict = st.session_state["data_dict"]

st.write("**Current SDRF file:**")
st.dataframe(template_df)
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
                 
# Ask the user to upload their own metadata file and to map it to the columns of the template file
metadata_file = st.file_uploader(
    "Upload your local metadata file (.csv, .tsv or .xls)", type=["csv", "tsv", "xlsx"])
if metadata_file is not None:
    ext = metadata_file.name.split(".")[-1]
    if ext == "csv":
        metadata_df = pd.read_csv(metadata_file)
    elif ext == "tsv":
        metadata_df = pd.read_csv(metadata_file, sep="\t")
    elif ext == "xlsx":
        metadata_df = pd.read_excel(metadata_file)

    st.dataframe(metadata_df)

    if metadata_df.shape[0] != template_df.shape[0]:
        st.error(f"Row count mismatch: metadata has {metadata_df.shape[0]}, SDRF has {template_df.shape[0]}.")

    # Initialize mapping_df ONCE
    if "mapping_df" not in st.session_state:
        st.session_state["mapping_df"] = pd.DataFrame({
            "Metadata column": metadata_df.columns.tolist(),
            "Mapped SDRF column": ["" for _ in metadata_df.columns]
        })

    # Display editable mapping table
    edited_mapping = st.data_editor(
        st.session_state["mapping_df"],
        column_config={
            "Mapped SDRF column": st.column_config.SelectboxColumn(
                "Mapped SDRF column",
                options=[""] + TEMPLATE_COLUMNS
            )
        },
        num_rows="fixed",
        use_container_width=True
    )

    # Store edits
    st.session_state["mapping_df"] = edited_mapping

    if st.button("🚀 Apply Mappings"):
        applied = False
        for _, row in st.session_state["mapping_df"].iterrows():
            meta_col = row["Metadata column"]
            sdrf_col = row["Mapped SDRF column"]
            if not sdrf_col:
                # st.warning(f"⚠️ '{meta_col}' not mapped")
                continue

            input_values = metadata_df[meta_col].dropna().unique()

            valid = False
            if sdrf_col == "characteristics[organism]":
                normalized_values = normalize_organism(input_values)
                name = "all_organism_elements"
                ontology_terms = data_dict.get(name, [])

                if set(normalized_values).issubset(ontology_terms):
                    st.success(f"✅ Mapped (normalized) '{meta_col}' → '{sdrf_col}'")
                    template_df[sdrf_col] = metadata_df[meta_col].replace(dict(zip(input_values, normalized_values)))
                    applied = True
                    valid = True
                else:
                    invalid_terms = set(normalized_values) - set(ontology_terms)
                    st.error(f"❌ {invalid_terms} not valid ontology terms after normalization for '{sdrf_col}'")

            elif sdrf_col in VALUE_COLUMNS:
                valid = True
            elif sdrf_col in OTHER_COLUMNS:
                if sdrf_col == "characteristics[age]":
                    valid = ParsingModule.check_age_format(metadata_df, meta_col)
                    if not valid:
                        st.error(f"❌ Invalid age format in '{meta_col}'")
                elif sdrf_col == "characteristics[sex]":
                    valid = all(val in ["M", "F", "NA"] for val in input_values)
                    if not valid:
                        st.error(f"❌ Invalid sex values in '{meta_col}' (expected M, F, NA)")
            else:
                name = f"all_{sdrf_col.split('[')[-1].split(']')[0].replace(' ', '_')}_elements"
                ontology_terms = data_dict.get(name, [])
                if ontology_terms:
                    if set(input_values).issubset(ontology_terms):
                        valid = True
                    else:
                        invalid_terms = set(input_values) - set(ontology_terms)
                        st.error(f"❌ {invalid_terms} not valid ontology terms for '{sdrf_col}'")
                else:
                    st.warning(f"⚠️ No ontology data found for {sdrf_col}, mapping skipped.")

            if valid and sdrf_col != "characteristics[organism]":
                st.success(f"✅ Mapped '{meta_col}' → '{sdrf_col}'")
                template_df[sdrf_col] = metadata_df[meta_col]
                applied = True

        if applied:
            st.session_state["template_df"] = template_df
            st.subheader("🎉 Updated SDRF preview")
            st.dataframe(template_df)

