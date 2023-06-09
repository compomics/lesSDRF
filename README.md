# lesSDRF

This github repository contains the code used to create the SDRF Streamlit application lesSDRF

The ontologies were downloaded in the format that was available and parsable.
In obo format:
PRIDE CV (version 2022-11-17) - PSI-MS (version 2022-09-26) - NCBITaxon (version 2022-08-18) 
In OWL format:
CL (version 2022-12-25) - HANCESTRO (version 2.6)
In JSON format:
EFO (version 3.49.0)
Data from the Unimod database for protein modifications was also copied in csv format from their website


The parsed ontologies used in the streamlit app are in the data folder. Every topic contains three types of data:
- all_elements: a list of every term in the ontology subset. Is used to check for ontology compatibility of local metadata.
- dict: a nested dictionary that follows the ontology tree structure
- nodes: a node like version of the nested dictionary according to the format required for the tree-select module: https://github.com/Schluca/streamlit_tree_select

To start the app you run: ** streamlit run Home.py **
This will then open the Home screen of the app. The following steps can be found in the pages folder and are numbered accordingly.
