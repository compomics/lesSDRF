import streamlit as st
import ParsingModule
import pandas as pd
import numpy as np
import re
import warnings
warnings.filterwarnings("ignore")
from streamlit_tree_select import tree_select


st.set_page_config(
    page_title="Additional columns",
    layout="wide",
    page_icon="🧪",
    menu_items={
        "Get help": "https://github.com/compomics/lesSDRF/issues",
        "Report a bug": "https://github.com/compomics/lesSDRF/issues",
    },
)


def update_session_state(df):
    st.session_state["template_df"] = df

def check_age_format(df, column):
    for index, row in df.iterrows():
        if (row[column] != "") and (row[column] != "empty") and (row[column] != "None"):
            st.write(row[column])
            if not re.match(r"^\d*Y\s\d*M\s\d*D$", row[column]):
                return False
    return True


st.title("""4. Additional columns""")
# Get filled in template_df from other page
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
unimod = st.session_state["unimod"]


all_possible_columns = [
    "characteristics[age]",
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
    "characteristics[enrichment process]",
    "characteristics[compound]",
    "characteristics[concentration of compound]",
    "comment[modification parameters]",
    "comment[cleavage agent details]",
    "comment[data file]",
    "comment[fraction identifier]",
    "comment[instrument]",
    "comment[label]",
    "comment[technical replicate]",
    "comment[fragment mass tolerance]",
    "comment[precursor mass tolerance]",
    "comment[dissociation method]",
    "comment[depletion]", 
    "comment[collision energy]"
]
# to still add:
    #"characteristics[phenotype]",
    #  "characteristics[spiked compound]",
    # characteristcs[mass]
    # "characteristics[synthetic peptide]",
    # 
def update_sidebar(df):
    #get columns from df that are not empty
    used_columns = df.columns[df.isnull().mean() < 1]
    additional_columns = sorted(set(all_possible_columns) - set(used_columns))
    return additional_columns


side_bar_columns = update_sidebar(template_df)
side_bar_columns.insert(0, "start")
side_bar_columns.insert(1, "factor value")
side_bar_columns.append("undo column")
with st.sidebar:
    selection = st.radio("These are all possible columns you may want to add:", side_bar_columns)
    download = st.download_button("Press to download SDRF file",ParsingModule.convert_df(template_df), "intermediate_SDRF.sdrf.tsv", help="download your SDRF file")


if selection == "start":
    st.write("""There are still columns that you can add to your SDRF file.  
    Similar to the previous section, you can select a column to annotate in the sidebar. When a column is filled, it will disappear from the sidebar so you can keep track on which columns you can still add.  
    When you want to reannotate a previously filled in column, you can do so by clicking on the **undo column** button in the sidebar.""")
    st.write(""" At the bottom of the page there are now two download buttons. The first one will download your intermediate SDRF file.   
    The second button will download your final SDRF file after some final checks. """)

if selection == "factor value":

    st.write(
        """You can choose one column that defines the **factor value** in your experiment.  \nThis column indicates which experimental factor/variable is used as the hypothesis to perform the data analysis.  \nIf there are multiple factor values, we suggest to make multiple SDRF files to avoid confusion concerning biological and technical replicates."""
    )
    col1, col2 = st.columns(2)
    with col1:
        factor_selection = st.multiselect("Select a factor value:", template_df.columns)
    with col2:

        save = st.checkbox("Save factor value?")
        if save:
            for i in factor_selection:
                st.write(i)
                fv_name = f"factor value[{i.split('[')[-1].split(']')[0]}]"
                # make a copy of the original column of i and store as new column called fv_name
                template_df[fv_name] = template_df[i]
                st.session_state["template_df"] = template_df
    st.write(template_df)

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
    st.subheader("Input the ages of your samples using the Years Months Days format, e.g. 1Y 2M 3D")
    multiple = st.selectbox(f"Are there multiple ages in your data?", ("","No", "Yes", "Not available"), help="If you select Not available, the column will be filled in with 'Not available'")
    if multiple == "Yes":
        template_df = ParsingModule.fill_in_from_list(template_df, "characteristics[age]")
        if check_age_format(template_df, "characteristics[age]") == False:
            st.error("The age column is not in the correct format, please check and try again")
            st.stop()
        elif check_age_format(template_df, "characteristics[age]") == True:
            st.success("The age column is in the correct format")
            update_session_state(template_df)
            st.experimental_rerun()
    if multiple == "No":
        age = st.text_input("Input the age of your sample in Y M D format e.g. 12Y 3M 4D", help="As you only have one age, the inputted age will be immediatly used to fill all cells in the age column")
        # check if the age is in Y M D format
        if (age != "") and (not re.match(r"^\d*Y\s\d*M\s\d*D$", age)):
            st.error("The age is not in the correct format, please check and try again",icon="🚨")
            st.stop()
        if (age != "") and (re.match(r"^\d*Y\s\d*M\s\d*D$", age)):
            st.write("The age is in the correct format")
            template_df["characteristics[age]"] = age
            update_session_state(template_df)
            st.experimental_rerun()  # reruns script, makes it unnecessary to click button twice
    if multiple == "Not available":
        template_df["characteristics[age]"] = "Not available"
        update_session_state(template_df)
        st.experimental_rerun()

if selection == "comment[alkylation reagent]":
    st.subheader("Input the alkylation reagent that was used in your experiment")
    all_alkylation_elements = data_dict["all_alkylation_elements"]
    alkylation_nodes = data_dict["alkylation_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_alkylation_elements, alkylation_nodes, template_df
    )
    update_session_state(df)

if selection == "characteristics[ancestry category]":
    st.subheader("Input the ancestry of your samples")
    all_ancestry_elements = data_dict["all_ancestry_category_elements"]
    ancestry_nodes = data_dict["ancestry_category_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_ancestry_elements, ancestry_nodes, template_df
    )
    update_session_state(df)


if selection == "characteristics[cell type]":
    # if the selection is not in the columns, add it as an empty column
    st.subheader("Input the cell type of your sample")
    all_cell_type = data_dict["all_cell_type_elements"]
    cell_type_nodes = data_dict["cell_type_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_cell_type, cell_type_nodes, template_df
    )
    update_session_state(df)

if selection == "characteristics[cell line]":
    st.subheader("Input the cell line of your sample if one was used")
    all_cellline = data_dict["all_cell_line_elements"]
    cellline_nodes = data_dict["cell_line_nodes"]
    df = ParsingModule.multiple_ontology_tree(selection, all_cellline, cellline_nodes, template_df, multiple_in_one=True)
    update_session_state(df)

if selection == "comment[cleavage agent details]":
    st.subheader("Input the cleavage agent details of your sample")
    cleavage_list = data_dict["all_cleavage_list_elements"]
    enzymes = st.multiselect(
        "Select the cleavage agents used in your sample If no cleavage agent was used e.g. in top down proteomics, choose *no cleavage*",
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
    if selection not in template_df.columns:
        template_df[selection] = np.nan
    st.subheader("If a compound was added to your sample, input the name here")
    compounds = []
    
    col1, col2, col3 = st.columns(3)
    index = template_df.columns.get_loc(selection)
    with col1:
        input_compounds = st.text_input("Input compound names as comma separated list")
    with col2:
        multiple_in_one_sel = st.radio("Are there multiple compounds within the same sample?", ("No", "Yes"))
    with col3:
        ready = st.checkbox('Ready?')
    if input_compounds is not None:
        input_compounds = re.sub(" ", "", input_compounds)
        input_compounds = input_compounds.split(",")
        compounds.append(input_compounds)
        compounds = compounds[0]
        st.write(compounds)
    if compounds and ready:
        if multiple_in_one_sel == "Yes":
            columns_to_adapt = []
            multiple_in_one = True
            for i in range(len(compounds)-1):
                # add column next to the original column if it is not already there
                if f"{selection}_{i+1}" not in template_df.columns:
                    template_df.insert(index+1, f"{selection}_{i+1}", "empty")
                columns_to_adapt.append(f"{selection}_{i+1}")
        else:
            multiple_in_one = False
        df = ParsingModule.fill_in_from_list(template_df, selection, compounds, multiple_in_one)
        update_session_state(df)
        st.experimental_rerun()


if selection == "characteristics[concentration of compound]": 
    if selection not in template_df.columns:
        template_df[selection] = np.nan
    st.subheader("Input the concentration with which the compound was added to your sample")
    concentration = []
    col1, col2, col3 = st.columns(3)
    index = template_df.columns.get_loc(selection)
    with col1:
        input_concentrations = st.text_input("Input compound concentrations as comma separated list")
    with col2:
        multiple_in_one_sel = st.radio("Are there multiple concentrations within the same sample?", ("No", "Yes"))
    with col3:
        ready = st.checkbox('Ready?')
    if input_concentrations is not None:
        input_concentrations = re.sub(" ", "", input_concentrations)
        input_concentrations = input_concentrations.split(",")
        concentration.append(input_concentrations)
        concentration = concentration[0]
        st.write(concentration)
    if concentration and ready:
        if multiple_in_one_sel == "Yes":
            columns_to_adapt = []
            multiple_in_one = True
            for i in range(len(concentration)-1):
                # add column next to the original column if it is not already there
                if f"{selection}_{i+1}" not in template_df.columns:
                    template_df.insert(index+1, f"{selection}_{i}", "empty")
                columns_to_adapt.append(f"{selection}_{i}")
        else:
            multiple_in_one = False
        df = ParsingModule.fill_in_from_list(template_df, selection, concentration, multiple_in_one)
        update_session_state(df)
        st.experimental_rerun()

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
        if coll_en:
            df = ParsingModule.fill_in_from_list(template_df, selection, values_list=[coll_en])
            update_session_state(df)
            st.experimental_rerun()

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
        selection, all_disease_type, disease_nodes, template_df, multiple_in_one = True
    )
    update_session_state(df)

if selection == "comment[dissociation method]":
    st.subheader("Input the dissociation method that was used in your experiment")
    all_dissociation_elements = data_dict["all_dissociation_elements"]
    dissociation_nodes = data_dict["dissociation_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_dissociation_elements, dissociation_nodes, template_df, multiple_in_one = True)
    update_session_state(df)

if selection == "characteristics[enrichment process]":
    st.subheader("Input the enrichment process that was used in your experiment")
    all_enrichment_elements = data_dict["all_enrichment_elements"]
    enrichment_nodes = data_dict["enrichment_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_enrichment_elements, enrichment_nodes, template_df, multiple_in_one = False
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
            number_of_fractions = 1

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
        sel = st.selectbox("Do you have multiple indiviuals in your data?", ("", "No", "Yes"))
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


if selection == "comment[label]":
    st.subheader("Input the label that was used in your experiment")
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
                            df.insert(index+1, f"{selection}_{i+1}", "empty")
                        columns_to_adapt.append(f"{selection}_{i+1}")
        if multiple == "No":
            number = 1
    
    col4, col5 = st.columns(2)
    with col4:
        st.write('Select your species using the tabs below. If you want to consult the ontology tree structure, you can click the button to the OLS search page.')
    with col5:
        url = "https://www.ebi.ac.uk/ols/ontologies/ncbitaxon"
        button = f'<a href="{url}" style="{button_styles}" id="mybutton" target="_blank">OLS NCBITaxon ontology tree</a>'    
        st.write(button, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(['Eukaryota', 'Archaea', 'Bacteria', 'Viruses', 'Unclassified', 'Other'])
    with tab1:
        eu_elem = data_dict["all_eukaryota_elements"]
        search_term = st.text_input("Search for an eukaryote species here", "")
        ret = ParsingModule.autocomplete_species_search(eu_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)

    with tab2:
        ar_elem = data_dict["all_archaea_elements"]
        search_term = st.text_input("Search for an archaea species here", "")
        ret = ParsingModule.autocomplete_species_search(ar_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)
    with tab3:
        ba_elem = data_dict["all_bacteria_elements"]
        search_term = st.text_input("Search for a bacteria species here", "")
        ret = ParsingModule.autocomplete_species_search(ba_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)
        
    with tab4:
        vi_elem = data_dict["all_virus_elements"]
        search_term = st.text_input("Search for a viral strain here", "")
        ret = ParsingModule.autocomplete_species_search(vi_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)
        
    with tab5:
        un_elem = data_dict["all_unclassified_elements"]
        search_term = st.text_input("Search for an unclassified species here", "")
        ret = ParsingModule.autocomplete_species_search(un_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)
        
    with tab6:
        other_elem = data_dict["all_other_sequences_elements"]
        search_term = st.text_input("Search for a species here", "")
        ret = ParsingModule.autocomplete_species_search(other_elem, search_term)
        if ret != None:
            #if ret is a list, add all elements to the set
            if isinstance(ret, list):
                for i in ret:
                    st.session_state.selected_species.add(i)
            else:
                st.session_state.selected_species.add(ret)

    st.write(st.session_state["selected_species"])       
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
    df = ParsingModule.fill_in_from_list(template_df, selection, list(st.session_state["selected_species"]), multiple_in_one)
    update_session_state(df)


if selection == "characteristics[organism part]":
    st.subheader("Select the part of the organism that is present in your sample")
    all_orgpart_elements = data_dict["all_organism_part_elements"]
    orgpart_nodes = data_dict["orgpart_nodes"]
    df = ParsingModule.multiple_ontology_tree(
        selection, all_orgpart_elements, orgpart_nodes, template_df
    )
    update_session_state(df)

if selection == "comment[reduction reagent]":
    st.subheader("Input the reduction reagent that was used in your experiment")
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
        template_df[selection] = "Not Available"
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
        st.write(biol_rep)
        template_df = ParsingModule.fill_in_from_list(template_df, selection, biol_rep)
        st.session_state["template_df"] = template_df
        #st.experimental_rerun()

if selection == "comment[fragment mass tolerance]":
    with st.form("Fragment mass tolerance"):
        col1, col2 = st.columns(2)
        with col1:
            multiple = st.radio(
                "Are there multiple fragment mass tolerances in your data?",
                ("Yes", "No"),
            )
        with col2:
            unit = st.radio(
                "Is the fragment mass tolerance in ppm or Da?", ("ppm", "Da")
            )
        s = st.form_submit_button("Input")

    if s and multiple == "Yes" and unit:
        st.write(
            "Input the fragment mass tolerance directly in the SDRF file (without unit)"
        )
        df = ParsingModule.fill_in_from_list(template_df, selection)
        df[selection] = df[selection].astype(str) + " " + str(unit)
        update_session_state(df)
        st.experimental_rerun()
    elif s and multiple == "No" and unit:
        fragment_mass = st.text_input("Input the fragment mass tolerance (without unit)")
        if fragment_mass:
            st.write(fragment_mass)
            if isinstance(fragment_mass, str):
                template_df[selection] = fragment_mass + " " + str(unit)
                st.session_state["template_df"] = template_df
                st.experimental_rerun()

if selection == "comment[precursor mass tolerance]":
    with st.form("Precursor mass tolerance"):
        col1, col2 = st.columns(2)
        with col1:
            multiple = st.radio(
                "Are there multiple precursor mass tolerances in your data?",
                ("Yes", "No"),
            )
        with col2:
            unit = st.radio(
                "Is the precursor mass tolerance in ppm or Da?", ("ppm", "Da")
            )
        s = st.form_submit_button("Input")

    if s and multiple == "Yes" and unit:
        st.write(
            "Input the precursor mass tolerance directly in the SDRF file (without unit)"
        )
        df = ParsingModule.fill_in_from_list(template_df, selection)
        df[selection] = df[selection].astype(str) + " " + str(unit)
        update_session_state(df)
        st.experimental_rerun()
    elif s and multiple == "No" and unit:
        precursor_mass = st.text_input(
            "Input the precursor mass tolerance (without unit)"
        )
        st.write(precursor_mass)
        if precursor_mass:
            if isinstance(precursor_mass, str):
                template_df[selection] = precursor_mass + " " + str(unit)
                st.session_state["template_df"] = template_df
                st.experimental_rerun()


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
    unimod = data_dict["unimod_dict"]
    inputs = sorted(list(unimod.keys()))
    inputs.append("Other")
    inputs.remove("#NAAM?")
    mt = ["Fixed", "Variable", "Annotated"]
    pp = ["Anwywhere", "Protein N-term", "Protein C-term", "Any N-term", "Any C-term"]
    ta = ["X","G","A","L","M","F","W","K","Q","E","S","P","V","I","C","Y","H","R","N","D","T"]
    mods_sel = st.multiselect("Select the modifications present in your data", inputs)
    sdrf_mods = []
    st.session_state["sdrf_mods"] = sdrf_mods

    for i in mods_sel:
        st.write(f"**{i}**")
        col1, col2, col3, col4 = st.columns(4)

        if i == "Other":
            with col1:
                name = st.text_input(
                    "Input a logical name for your custom modification"
                )
            with col2:
                form = st.text_input("Input the chemical formula of the modification")
            with col3:
                mass = st.text_input("Input the mass of the modification")
            with col4:
                final_str = f"NT={name};CF={form};MM={mass}"
                st.write(
                    f""" **Final SDRF notation of modification:**  
                 {final_str}"""
                )
                done = st.button(
                    "Okay",
                    key=f"done_{i}",
                    help="Click to add the modification to the SDRF file",
                    on_click=st.session_state["sdrf_mods"].append(final_str),
                )

        else:
            with col1:
                mt_sel = st.selectbox("Select the modification type", mt, key=f"mt_{i}")
            with col2:
                pp_sel = st.selectbox(
                    "Select the position of the modification", pp, key=f"pp_{i}"
                )
            with col3:
                ta_sel = st.selectbox("Select the target amino acid", ta, key=f"ta_{i}")
            with col4:
                final_str = f"{unimod[i]};MT={mt_sel};PP={pp_sel};TA={ta_sel}"
                st.write(
                    f"""**Final SDRF notation of modification:**  
                    {final_str}"""
                )
                done = st.button(
                    "Okay",
                    key=f"done_{i}",
                    help="Click to add the modification to the SDRF file",
                    on_click=st.session_state["sdrf_mods"].append(final_str),
                )

    submit = st.checkbox(
        "Submit modifications",
        help="Click to add the modifications to the SDRF file. If everything looks fine, click again",
    )

    if submit:
        # for every element in the list sdrf_mods
        # add it to the template_df as a value in a new column with name selection_1, selection_2, selection_3, etc
        # then update the session state
        for i, mod in enumerate(sdrf_mods):
            st.write(i, mod)
            template_df[f"{selection}_{i}"] = mod
        template_df.drop(columns=[selection], inplace=True)
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
            
            side_bar_columns = update_sidebar(template_df)  
            st.session_state["template_df"] = template_df
            st.experimental_rerun()


