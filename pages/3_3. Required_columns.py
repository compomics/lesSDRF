import re
import warnings
warnings.filterwarnings("ignore")
import streamlit as st
import pandas as pd
import numpy as np
import json
import gzip
import ParsingModule
import os
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
from streamlit_tree_select import tree_select
from PIL import Image
import base64
import io

st.set_page_config(
    page_title="Required columns",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)
def add_logo(logo_path, width, height):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo

def get_base64_image(image):
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return img_str

my_logo = add_logo(logo_path="final_logo.png", width=149, height=58)

st.markdown(
    f"""
    <style>
        [data-testid="stSidebarNav"] {{
            background-image: url('data:image/png;base64,{get_base64_image(my_logo)}');
            background-repeat: no-repeat;
            background-position: 40px 20px;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

def update_session_state(df):
    st.session_state["template_df"] = df

@st.cache_data
def load_organism_data():
    #find dir one up from current dir
    data_dir = os.path.dirname(os.path.dirname(__file__))
    folder_path = os.path.join(data_dir, "data")
    data = {}
    for filename in os.listdir(folder_path):
        # only load the files containing the following names: archae, bacteria, eukaryota, virus, unclassified, other sequences
        if re.search(r"archaea|bacteria|eukaryota|virus|unclassified|other_sequences", filename):
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
        else:
            continue
    return data

def organism_selection(species):
    lem = organism_data[f"all_{species}_elements"]
    search_term = st.text_input(f"Search for an {species} species here", "")
    ret = ParsingModule.autocomplete_species_search(lem, search_term)
    if ret != None:
        return ret

# Define the default button color (you can adjust this as desired)
default_color = "#ff4b4b"

# Define the button CSS styles
button_styles = f"""
    background-color: white;
    color: {default_color};
    border-radius: 20px;
    padding: 10px 20px;
    border: 1px solid {default_color};
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 4px 2px;
    cursor: pointer;
"""
st.title("""3. Required columns""")
# if template_df is not in the session state, don't run all the code below
if "template_df" not in st.session_state:
    st.error("Please fill in the template file in the Home page first", icon="🚨")  
    st.stop()
else:
    template_df = st.session_state["template_df"] 
    with st.container():
        st.write("**This is your current SDRF file.**")
        st.dataframe(template_df)

data_dict = st.session_state["data_dict"]
#get all columns that are empty or contain only the word "empty" in template_df
empty_columns = [col for col in template_df.columns if template_df[col].isnull().all() or (template_df[col] == "empty").all()]
#remove columns from the list that have an underscore in the name(these are added because of multiple in one samples)
empty_columns = [col for col in empty_columns if "_" not in col]
empty_columns.append('undo column')
empty_columns.insert(0, 'start')




with st.sidebar:
    selection = st.radio(
        "The following columns are empty and required",
        empty_columns, help="If a column you're looking for is not in this display, This means it is not empty. Click on the 'undo column' button and empty your column of interest."
    )
    download = st.download_button("Press to download SDRF file",ParsingModule.convert_df(template_df), "intermediate_SDRF.sdrf.tsv", help="download your SDRF file")
    st.write("""Please refer to your data and lesSDRF within your manuscript as follows:
                 *The experimental metadata has been generated using lesSDRF and is available through ProteomeXchange with the dataset identifier [PXDxxxxxxx]*""")

if selection == 'start':
    st.write("""In the sidebar, all the empty columns that are required for you SDRF file are listed. Select the one you want to annotate first.  
    When a column is filled in, it will disappear from the sidebar so you can keep track on which columns still require input.  
    When you want to reannotate a previously filled in column, you can do so by clicking on the **undo column** button in the sidebar.  
    """)
    st.write("""Every page will start with your current SDRF file and at the bottom of the page there is a button to download the intermediate SDRF file""")





if selection == "source name":
    st.write(
        """The source name is the unique sample name (it can be present multiple times if the same sample is used several times in the same dataset) eg. healthy_patient_1, diseased_patient_1
    If you did not add it using the previous mapping function, you can input it here manually.")  
    """
    )
    st.write(
        "Type the correct source names in the corresponding column and **double click** *Update* when finished"
    )
    template_df = ParsingModule.fill_in_from_list(template_df, "source name")
    st.session_state["template_df"] = template_df


if selection == "assay name":
    st.write(
        """The assay name is a name for the run file, this has to be a uniqe value eg. run 1 - run 2 - run 3_fraction1. If you did not add it using the previous mapping function, you can input it here 
        manually."""
    )
    st.write(
        "Type the correct assay names in the corresponding column and click Update twice when finished"
    )
    template_df = ParsingModule.fill_in_from_list(template_df, "assay name")
    st.session_state["template_df"] = template_df
    
if selection == "technology type":
    with st.form("Choose the technology type in your sample"):
        tech_type = st.radio(
            "Choose the technology type from these options:",
            (
                "proteomic profiling by mass spectrometry",
                "metabolomics profiling by mass spectrometry",
                "other",
            ),
        )
        if st.form_submit_button("Submit"):
            template_df["technology type"] = tech_type
    st.session_state["template_df"] = template_df

if selection == "characteristics[age]":
    st.subheader("Input the ages of your samples using the Years Months Days format, e.g. 1Y 2M 3D. Age ranges should be formatted as e.g. 1Y-3Y")
    multiple = st.selectbox(f"Are there multiple ages in your data?", ("","No", "Yes", "Not available"), help="If you select Not available, the column will be filled in with 'Not available'")
    if multiple == "Yes":
        template_df = ParsingModule.fill_in_from_list(template_df, "characteristics[age]")
        is_valid, wrong_values = ParsingModule.check_age_format(template_df, "characteristics[age]") 
        if not is_valid:
            st.error(f"The age column is not in the correct format. Wrong values: {', '.join(wrong_values)}")
            st.stop()
        else:
            template_df.replace("empty", np.nan, inplace=True)
            st.success("The age column is in the correct format")
            update_session_state(template_df)
            st.experimental_rerun()
    if multiple == "No":
        age = st.text_input("Input the age of your sample in Y M D format e.g. 12Y 3M 4D", help="As you only have one age, the inputted age will be immediatly used to fill all cells in the age column")
        # Check if the age is in Y M D format or age range format

        if age:
            if not (re.match(r"^(\s*\d+\s*Y)?(\s*\d+\s*M)?(\s*\d+\s*D)?(|\s*-\s*\d+\s*Y)?(|\s*-\s*\d+\s*M)?(|\s*-\s*\d+\s*D)?(/)?(|\s*\d+\s*Y)?(|\s*\d+\s*M)?(|\s*\d+\s*D)?$", age)):
                st.error("The age is not in the correct format, please check and try again",icon="🚨")
                st.stop()
            else:
                st.write("The age is in the correct format")
                template_df["characteristics[age]"] = age
                update_session_state(template_df)
                st.experimental_rerun()
    if multiple == "Not available":
        template_df["characteristics[age]"] = "Not available"
        update_session_state(template_df)
        st.experimental_rerun()
        
if selection == "comment[alkylation reagent]":
    st.subheader("Input the alkylation reagent that was used in your experiment")
    all_alkylation_elements = data_dict["all_alkylation_elements"]
    alkylation_nodes = data_dict["alkylation_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_alkylation_elements, alkylation_nodes, template_df, multiple_in_one=True)
    update_session_state(df)

if selection == "characteristics[ancestry category]":
    st.subheader("Input the ancestry of your samples")
    all_ancestry_elements = data_dict["all_ancestry_category_elements"]
    ancestry_nodes = data_dict["ancestry_category_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_ancestry_elements, ancestry_nodes, template_df, multiple_in_one=False)
    update_session_state(df)


if selection == "characteristics[cell type]":
    st.subheader("Input the cell type of your sample")
    all_cell = data_dict["all_cell_elements"]
    cell_nodes = data_dict["cell_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_cell, cell_nodes, template_df, multiple_in_one=True)
    update_session_state(df)

if selection == "characteristics[cell line]":
    st.subheader("Input the cell line of your sample if one was used")
    all_cellline = data_dict["all_cell_line_elements"]
    cellline_nodes = data_dict["cell_line_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_cellline, cellline_nodes, template_df,multiple_in_one=True)
    update_session_state(df)

if selection == "comment[cleavage agent details]":
    st.subheader("Input the cleavage agent details of your sample")
    cleavage_list = data_dict["cleavage_list"]
    enzymes = st.multiselect(
        "Select the cleavage agents used in your sample If no cleavage agent was used e.g. in top down proteomics, choose *NoEnzyme*",
        cleavage_list,
    )
    s = st.checkbox("Ready for input?")   
    if s and len(enzymes) == 1:
        template_df[selection] = enzymes[0]
        st.experimental_rerun()
    if s:
        df = ParsingModule.fill_in_from_list(template_df, selection, enzymes)
        update_session_state(df)

if selection == "characteristics[compound]":
    st.subheader("If a compound was added to your sample, input the name here")
    compounds = []
    input_compounds = st.text_input("Input compound names as comma separated list")
    if input_compounds is not None:
        input_compounds = re.sub(" ", "", input_compounds)
        input_compounds = input_compounds.split(",")
        compounds.append(input_compounds)
        compounds = compounds[0]
        st.write(compounds)
    if compounds != [""]:
        template_df = ParsingModule.fill_in_from_list(template_df, selection, compounds)
        st.session_state["template_df"] = template_df

if selection == "characteristics[concentration of compound]":
    st.subheader("Input the concentration with which the compound was added to your sample")
    concentration = []
    input_concentration = st.text_input(
        "Input compound concentration as comma separated list, don't forget to indicate the unit"
    )
    if input_concentration is not None:
        input_concentration = re.sub(" ", "", input_concentration)
        input_concentration = input_concentration.split(",")
        concentration.append(input_concentration)
        concentration = concentration[0]
    st.write(concentration)
    if concentration != [""]:
        template_df["characteristics[concentration of compound]"] = ""
        template_df = ParsingModule.fill_in_from_list(
            template_df, selection, concentration
        )
        st.session_state["template_df"] = template_df


if selection == "comment[collision energy]":
    st.subheader("Input the collision energy that was used in your experiment")
    multiple = st.radio(
        f"Are there multiple collision energies in your data?", ("No", "Yes")
    )
    if multiple == "Yes":
        st.write(
            "Input the collision energy directly in the SDRF file. Don't forget to indicate the unit"
        )
        df = ParsingModule.fill_in_from_list(template_df, selection)
        update_session_state(df)
    else:
        coll_en = st.text_input("Input the collision energy and its unit")
        template_df[selection] = coll_en
        st.session_state["template_df"] = template_df

if selection == "characteristics[developmental stage]":
    st.subheader("Input the developmental stage of your sample")
    all_devstage = data_dict["all_developmental_stage_elements"]
    devstage_nodes = data_dict["developmental_stage_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_devstage, devstage_nodes, template_df, multiple_in_one=False)
    update_session_state(df)
    
if selection == "characteristics[disease]":
    st.subheader("If you have healthy and control samples, indicate healthy samples using *normal*. Input the disease for the other samples using the ontology")
    all_disease_type = data_dict["all_disease_elements"]
    disease_nodes = data_dict["disease_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_disease_type, disease_nodes, template_df
    )
    update_session_state(df)

if selection == "comment[dissociation method]":
    st.subheader("Input the dissociation method that was used in your experiment")
    all_dissociation_elements = data_dict["all_dissociation_elements"]
    dissociation_nodes = data_dict["dissociation_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_dissociation_elements, dissociation_nodes, template_df, multiple_in_one=True)
    update_session_state(df)

if selection == "characteristics[enrichment process]":
    st.subheader("Input the enrichment process that was used in your experiment")
    all_enrichment_elements = data_dict["all_enrichment_elements"]
    enrichment_nodes = data_dict["enrichment_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_enrichment_elements, enrichment_nodes, template_df
    )
    update_session_state(df)

if selection == "comment[fraction identifier]":
    # first ask if they have fractionation
    # if they don't ==> fraction identifier = 1
    # if they do: add fraction identifiers + add fractionation method
    number_of_fractions = None
    col1, col2 = st.columns(2)
    with col1:
        multiple = st.selectbox(
            f"Are there multiple fractions in your data?", ("", "No", "Yes")
        )
        number_of_methods = None
        if multiple == "Yes":
            with col2:
                number_of_fractions = st.number_input(
                    f"How many different fractions are in your data?",
                    min_value=0,
                    step=1,
                )
                number_of_methods = st.number_input(
                    f"How many different fractionation methods are used?",
                    min_value=0,
                    step=1,
                )
        if multiple == "No":
            template_df["comment[fraction identifier]"] = 1
    if number_of_methods:
        with st.form("Provide details on the fractionation method"):
            # template_df["comment[ fractionation method]"] = ""
            fractionation_elements = data_dict["all_fractionation_method_elements"]
            fractionation_nodes = data_dict["fractionation_nodes"]
            col3, col4 = st.columns(2)
            with col3:
                # selectbox with search option
                fractionation_elements.append(" ")
                fractionation_elements = set(fractionation_elements)
                return_search = st.multiselect(
                    "Select your matching fractionation term using this autocomplete function",
                    fractionation_elements,
                    max_selections=number_of_methods,
                )
            with col4:
                st.write("Or follow the ontology based drop down menu below")
                return_select = tree_select(
                    fractionation_nodes,
                    no_cascade=True,
                    expand_on_click=True,
                    check_model="leaf",
                )

            if (len(return_select["checked"]) > 1) & (
                len(return_select["checked"]) != number_of_methods
            ):
                st.error(f"You need to select a total of {number_of_methods}.")
            all = return_search + return_select["checked"]
            all = [i.split(",")[-1] for i in all if i is not None]
            if (len(all) >= 1) & (len(all) != number_of_methods):
                st.error(f"You need to select a total of {number_of_methods}.")
            x = st.form_submit_button("Submit selection")
            if x:
                st.write(f"Selection contains: {all}")

        if x:
            df = ParsingModule.fill_in_from_list(template_df, "comment[fractionation method]", all)
            df = ParsingModule.fill_in_from_list(template_df, "comment[fraction identifier]", [*range(1, number_of_fractions + 1)])
            update_session_state(df)

if selection == "comment[instrument]":
    st.subheader("Input the instrument that was used in your experiment")
    all_instrument_elements = data_dict["all_instrument_elements"]
    instrument_nodes = data_dict["instrument_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_instrument_elements, instrument_nodes, template_df
    )
    update_session_state(df)

if selection == "characteristics[individual]":
    col1, col2, col3 = st.columns(3)
    with col1:
        sel = st.selectbox("Do you have multiple indiviuals in your data?", ("", "No", "Yes", "Not available"))
        if sel == "No":
            template_df[selection] = 1
            st.session_state["template_df"] = template_df
            st.experimental_rerun()
        if sel == "Yes":
            with col2:
                number = st.number_input("How many indiviuals are in your data?", min_value=0, step=1)
            with col3:
                s = st.checkbox("Ready for input?")
    if sel == "Yes" and s:
        indiv = [*range(1, number + 1, 1)]
        df = ParsingModule.fill_in_from_list(template_df, "characteristics[individual]", indiv)
        update_session_state(df)
    if sel == "Not available":
        template_df[selection] = "Not available"
        st.session_state["template_df"] = template_df
        st.experimental_rerun()


if selection == "comment[label]":
    st.subheader("Input the label that was used in your experiment. If no label was added, indicate this using *label free sample*.")
    all_label_elements = data_dict["all_label_elements"]
    label_nodes = data_dict["label_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_label_elements, label_nodes, template_df
    )
    update_session_state(df)

if selection == "characteristics[organism]":
    if "selected_species" not in st.session_state:
        st.session_state["selected_species"] = set()
    st.subheader("Select the species that is present in your sample")
    if selection not in template_df.columns:
        template_df[selection] = np.nan
    multiple_in_one = False
    index = template_df.columns.get_loc(selection)
    col1, col2, col3, col4 = st.columns(4)
    columns_to_adapt = [selection]
    with col1:
        multiple = st.radio(f"Are there multiple organisms in your data?", ("No", "Yes"))
        if multiple == "Yes":
            with col2:
                number = st.number_input(
                    f"How many different organisms are in your data?",
                    min_value=0,
                    step=1)
            with col3:
                multiple_in_one_sel = st.radio(f"Are there multiple organisms within one sample?", ("No", "Yes"))     
                if multiple_in_one_sel == "Yes":
                    multiple_in_one = True
                    for i in range(number-1):
                        # add column next to the original column if it is not already there
                        if f"{selection}_{i+1}" not in template_df.columns:
                            template_df.insert(index+1, f"{selection}_{i+1}", "empty")
                        columns_to_adapt.append(f"{selection}_{i+1}")
        if multiple == "No":
            number = 1
    
    col6, col7 = st.columns(2)
    with col6:
        model = st.radio('Does your data contain only classical model organisms?', ('Yes', 'No'), 
        help="Classical model organism being: Homo sapiens, Mus musculus, Drosophila Melanogaster, Arabidopsis thaliana, Xenopus laevis,  Xenopus tropicalis, Saccharomyces cerevisiae, Caenorhabditis elegans, Danio rerio, Escherichia coli and Cavia porcellus")
        classical_model_organisms = ["Homo sapiens",  
        "Mus musculus",  
        "Drosophila Melanogaster",  
        "Arabidopsis thaliana",  
        "Xenopus laevis", "Xenopus tropicalis",
        "Saccharomyces cerevisiae",
        "Caenorhabditis elegans", 
        "Danio rerio", 
        "Escherichia coli", 
        "Cavia porcellus"]
    if model == 'Yes':
        with col7:
            sel = st.multiselect('Select the classical model organism here', classical_model_organisms, max_selections=number)
            if isinstance(sel, list):
                for i in sel:
                    if i is not None:
                        st.session_state.selected_species.add(i)
            else:
                if sel is not None:
                    st.session_state.selected_species.add(sel)
    if model == 'No':
        st.write('The NCBITaxon ontology data is loaded. Please allow a few seconds for the data to be loaded. ')
        organism_data = load_organism_data()
        if organism_data:
            st.success(f"*NCBITaxon organism data was loaded*", icon="✅")
        else:
            st.error("Failed loading data", icon="❌")
        st.write("""First, select your species type using the tabs below.  
        Then you can fill in the name of your species and suggested ontology terms will appear, from which you can select the correct term or the perfectly matched term.  
        If you want to consult the ontology tree structure, you can click the button below to the OLS search page.""")
        url = "https://www.ebi.ac.uk/ols/ontologies/ncbitaxon"
        button = f'<a href="{url}" style="{button_styles}" id="mybutton" target="_blank">OLS NCBITaxon ontology tree</a>'    
        st.write(button, unsafe_allow_html=True)        

        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Eukaryota', 'Archaea', 'Bacteria', 'Viruses', 'Unclassified', 'Other'])
        with tab1:
            ret= organism_selection("eukaryota")
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)
        with tab2:
            ret= organism_selection("archaea")
            if ret != None:
                #if ret is a list, add all elements to the set
                if isinstance(ret, list):
                    for i in ret:
                        st.session_state.selected_species.add(i)
                else:
                    st.session_state.selected_species.add(ret)
        with tab3:
            ret= organism_selection("bacteria")
            if ret != None:
                #if ret is a list, add all elements to the set
                if isinstance(ret, list):
                    for i in ret:
                        st.session_state.selected_species.add(i)
                else:
                    st.session_state.selected_species.add(ret)
            
        with tab4:
            ret= organism_selection("virus")
            if ret != None:
                #if ret is a list, add all elements to the set
                if isinstance(ret, list):
                    for i in ret:
                        st.session_state.selected_species.add(i)
                else:
                    st.session_state.selected_species.add(ret)
            
        with tab5:
            ret= organism_selection("unclassified")
            if ret != None:
                #if ret is a list, add all elements to the set
                if isinstance(ret, list):
                    for i in ret:
                        st.session_state.selected_species.add(i)
                else:
                    st.session_state.selected_species.add(ret)
            
        with tab6:
            ret= organism_selection("other_sequences")
            if ret != None:
                #if ret is a list, add all elements to the set
                if isinstance(ret, list):
                    for i in ret:
                        st.session_state.selected_species.add(i)
                else:
                    st.session_state.selected_species.add(ret)
    if st.session_state['selected_species'] != {None}:
        st.write(f"You selected the following species:{st.session_state['selected_species']}")       
    if len(st.session_state["selected_species"]) > number:
        st.error(f"""Number of selected species is {len(st.session_state['selected_species'])}, but this should be {number} according to the input above. 
        Select the species you cant to remove from the list below""")
        # checkbox to remove species
        remove_species = set()
        for i, element in enumerate(st.session_state["selected_species"]):
            if st.checkbox(f"{element}", key=i):
                remove_species.add(element)
        st.session_state["selected_species"] = st.session_state["selected_species"] - remove_species
        st.write(f"Selected species after removal: {st.session_state['selected_species']}")
    elif (len(st.session_state["selected_species"]) < number) and (len(st.session_state["selected_species"]) > 0):
        st.error(f"""Number of selected species is {len(st.session_state['selected_species'])}, but this should be {number} according to the input above.
        Please select {number-len(st.session_state['selected_species'])} more organisms.""")
    s = st.checkbox("Ready for input?")
    if s:
        input_list = list(st.session_state["selected_species"])
        if multiple_in_one:
            #add "" in the beginning of the list
            input_list.insert(0, "NA")
        df = ParsingModule.fill_in_from_list(template_df, selection, input_list, multiple_in_one)
        update_session_state(df)
        #remove the session state
    del st.session_state["selected_species"]
    #remove the organism_data from the session state

if selection == "characteristics[organism part]":
    st.write("Select the part of the organism that is present in your sample")
    all_orgpart_elements = data_dict["all_organism_part_elements"]
    orgpart_nodes = data_dict["organism_part_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_orgpart_elements, orgpart_nodes, template_df, multiple_in_one=True
    )
    update_session_state(df)

if selection == "comment[reduction reagent]":
    st.write("Input the reduction reagent that was used in your experiment")
    all_reduction_elements = data_dict["all_reduction_reagent_elements"]
    reduction_nodes = data_dict["reduction_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_reduction_elements, reduction_nodes, template_df
    )
    update_session_state(df)

if selection == "characteristics[sex]":
    col1, col2, col3 = st.columns(3)
    with col1:
        sel = st.selectbox("Are there multiple sexes in your data?", ("", "No", "Yes", "Not available"))
    if sel == "No":
        sel2 = st.selectbox("Select the sex of your sample", ("", "F", "M", "unknown"))
        if sel2 in ["F", "M", "unknown"]:
            template_df[selection] = sel2
            st.session_state["template_df"] = template_df
            st.experimental_rerun()
    if sel == "Yes":
        df = ParsingModule.fill_in_from_list(template_df, "characteristics[sex]", ["F", "M", "unknown"])
        update_session_state(df)
    if sel == "Not available":
        template_df[selection] = "Not available"
        st.session_state["template_df"] = template_df
        st.experimental_rerun()

if selection == "comment[technical replicate]":
    col1, col2, col3 = st.columns(3)
    with col1:
        sel = st.selectbox("Do you have technical replicates?", ("", "Yes", "No"))
        if sel == "No":
            template_df[selection] = 1
            st.session_state["template_df"] = template_df
            st.experimental_rerun()
        if sel == "Yes":
            with col2:
                number = st.number_input("How many technical replicates are in your data?", min_value=0, step=1)
            with col3:
                s = st.checkbox("Ready for input?")
    if sel== "Yes" and s:
        tech_rep = [*range(1, number + 1, 1)]
        df = ParsingModule.fill_in_from_list(template_df, selection, tech_rep)
        update_session_state(df)



if selection == "characteristics[biological replicate]":
    col1, col2, col3 = st.columns(3)
    with col1:
        sel = st.selectbox("Do you have biological replicates?", ("", "Yes", "No"))
        if sel == "No":
            template_df[selection] = 1
            st.session_state["template_df"] = template_df
            st.experimental_rerun()
        if sel == "Yes":
            with col2:
                number = st.number_input("How many biological replicates are there?", min_value=0, step=1)
            with col3:
                s = st.checkbox("Ready for input?")
    if sel== "Yes" and s:
        biol_rep = [*range(1, int(number) + 1, 1)]
        template_df = ParsingModule.fill_in_from_list(template_df, selection, biol_rep)
        st.session_state["template_df"] = template_df
        #st.experimental_rerun()

if selection == "comment[fragment mass tolerance]":
    st.subheader(""" Input the fragment mass tolerance and **the unit (ppm or Da)**. click Update twice when finished""")
    df = ParsingModule.fill_in_from_list(template_df, selection)
    update_session_state(df)

if selection == "comment[precursor mass tolerance]":
    st.subheader(""" Input the precursor mass tolerance and **the unit (ppm or Da)**. click Update twice when finished""")
    df = ParsingModule.fill_in_from_list(template_df, selection)
    update_session_state(df)
  


if selection == "characterics[synthetic peptide]":
    st.subheader(
        "If the sample is a synthetic peptide library, indicate this by selecting *synthetic* or *not synthetic*"
    )
    df = ParsingModule.fill_in_from_list(
        template_df, selection, ["synthetic", "not synthetic"]
    )
    update_session_state(df)

if selection == "comment[depletion]":
    depl = st.selectbox("Is the sample depleted?", ("","Yes", "No"))
    if depl == "Yes":
        st.write("Indicate depleted or bound fraction directly in the SDRF file")
        df = ParsingModule.fill_in_from_list(
            template_df, selection, ["depleted fraction", "bound fraction"]
        )
        update_session_state(df)
    if depl == "No":
        template_df["comment[depletion]"] = "not depletion"
        st.session_state["template_df"] = template_df
        st.experimental_rerun()

if selection == "comment[modification parameters]":
    st.write(""" First select the modifications that are in your sample using the drop down autocomplete menu. After selection you will need to choose the modification type, position and target amino acid.  
    Modification type can be fixed, variable or annotated. Annotated is used to search for all the occurrences of the modification into an annotated protein database file like UNIPROT XML or PEFF.  
    Position can be anywhere, protein N-term, protein C-term, any N-term or any C-term.  
    Target amino acid can be any amino acid or X if it's not in the list. Yoy can also select multiple amino acids.""")
    st.write(""" If the modification  of your choice is not available in the drop down list, select "Other" and input the modification name, chemical formula and mass of your custom modification.""")
    st.write(""" The final modification will be formatted following the SDRF guidelines after which you can click on "Submit modifications".""")
    unimod = data_dict["unimod_dict"]
    inputs = sorted(list(unimod.keys()))
    inputs.append("Other")
    mt = ["Fixed", "Variable", "Annotated"]
    pp = ["Anywhere", "Protein N-term", "Protein C-term", "Any N-term", "Any C-term"]
    ta = ["X","G","A","L","M","F","W","K","Q","E","S","P","V","I","C","Y","H","R","N","D","T"]
    mods_sel = st.multiselect("Select the modifications present in your data", inputs)
    sdrf_mods = []
    st.session_state["sdrf_mods"] = sdrf_mods

    for i in mods_sel:
        st.write(f"**{i}**")
        col1, col2, col3 = st.columns(3)


        with col1:
            mt_sel = st.selectbox("Select the modification type", mt, key=f"mt_{i}")
        with col2:
            pp_sel = st.selectbox(
                "Select the position of the modification", pp, key=f"pp_{i}"
            )
        with col3:
            ta_sel = st.multiselect("Select the target amino acid", ta, key=f"ta_{i}")

        if i == "Other":
            col4, col5, col6 = st.columns(3)
            with col4:
                name = st.text_input(
                    "Input a logical name"
                )
            with col5:
                form = st.text_input("Input the chemical formula")
            with col6:
                mass = st.text_input("Input the molecular mass")

            final_str = f"NT={name};MT={mt_sel};PP={pp_sel};TA={ta_sel};CF={form};MM={mass}"
            st.session_state["sdrf_mods"].append(final_str)
            st.write(
                f""" **Final SDRF notation of modification:**  
                {final_str}"""
            )
        else:
            final_str = f"{unimod[i]};MT={mt_sel};PP={pp_sel};TA={ta_sel}"
            st.session_state["sdrf_mods"].append(final_str)
            st.write(
                f"""**Final SDRF notation of modification:**  
                {final_str}"""
            )
    st.write(f"Confirmed modifications contain: {st.session_state['sdrf_mods']}")
    submit = st.checkbox(
        "Submit modifications",
        help="Click to add the modifications to the SDRF file. If everything looks fine, click again",
    )

    if submit:
        # for every element in the list sdrf_mods
        # add it to the template_df as a value in a new column with name selection_1, selection_2, selection_3, etc
        # then update the session state
        #get the index of the original column
        index = template_df.columns.get_loc(selection)
        #insert the new column next to the original index
        for i, mod in enumerate(sdrf_mods):
            st.write(i, mod)
            if i == 0:
                template_df[f"{selection}"] = mod
            else:
                template_df.insert(index+i, f"{selection}_{i}", mod)
                index += 1
    
        st.session_state["template_df"] = template_df
    st.write(template_df)

if selection == "undo column":
    st.write("""Here you can select a column that you want to reannotate.   
    Upon clicking the column the current values will be removed and you can reannotate the column.   
    """)
    col1, col2 = st.columns(2)
    with col1:
        sel = st.multiselect("Select the column(s) you want to reannotate", template_df.columns)
    with col2:
        if st.button("Reannotate"):
            template_df[sel] = np.nan
            st.session_state["template_df"] = template_df
            st.experimental_rerun()

