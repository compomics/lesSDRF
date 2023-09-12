# lesSDRF

This github repository contains the code used to create the lesSDRF application which is available via https://lessdrf.streamlit.app/
A manual on the tool in pdf format is available here: https://github.com/compomics/lesSDRF/blob/main/lesSDRF_manual.pdf

The parsed ontologies used in the streamlit app are in the data folder. Every topic contains three types of data:
- all_elements: a list of every term in the ontology subset. Is used to check for ontology compatibility of local metadata.
- dict: a nested dictionary that follows the ontology tree structure
- nodes: a node like version of the nested dictionary according to the format required for the tree-select module: https://github.com/Schluca/streamlit_tree_select

To start the app locally you run: ** streamlit run Home.py **
This will then open the Home screen of the app. The following steps can be found in the pages folder and are numbered accordingly.

### lesSDRF v0.1.0 has the following ontologies incorporated:

    Streamlit version 1.19.0 and Python version 3.9.13
    
    PRIDE CV (version 2022-11-17)
    
    PSI-MS (version 2022-09-26) and NCBITaxon (version 2022-08-18) in obo format
    
    CL (version 2022-12-25) and HANCESTRO (version 2.6) in OWL format
    
    and EFO (version 3.49.0) in JSON format. 
