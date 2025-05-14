# common.py
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
import os

def add_logo(logo_path="final_logo.png", width=149, height=58):
    """Read and return a resized logo"""
    logo = Image.open(logo_path)
    modified_logo = logo.resize((width, height))
    return modified_logo

def get_base64_image(image):
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return img_str

def inject_sidebar_logo(logo_path="final_logo.png", width=149, height=58):
    my_logo = add_logo(logo_path, width, height)
    encoded_logo = get_base64_image(my_logo)

    st.markdown(
        f"""
        <style>
            [data-testid="stSidebarNav"] {{
                background-image: url("data:image/png;base64,{encoded_logo}");
                background-repeat: no-repeat;
                background-position: 20px 20px;
                padding-top: 80px;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
