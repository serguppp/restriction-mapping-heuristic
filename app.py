import streamlit as st
import subprocess
import json
import time
from components.button import Button
from components.runner import CppRunner

CPP_EXE_PATH = "./src/main"
# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="centered")
st.title("Restriction Mapping Heuristics")

# UI
st.sidebar.header("Input Parameters")
m = st.sidebar.slider("P size", min_value=5, max_value=100, value=10)
max_val = st.sidebar.number_input("Max Distance Value", min_value=10, max_value=1000, value=100)

if "p_points" not in st.session_state:
    st.session_state.p_points = []
if "d_distances" not in st.session_state:
    st.session_state.d_distances = []
if "success_msg" not in st.session_state:
    st.session_state.success_msg = ""

if st.session_state.success_msg:
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = ""

col1, col2 = st.columns(2)
                
with col1:
    st.subheader("Generated P Points")
    #p_points = json.dumps(st.session_state.p_points) if st.session_state.p_points else ""
    p_points = ", ".join(map(str, st.session_state.p_points)) if st.session_state.p_points else ""
    p_text_area = st.text_area(
        label = "Generated P Points",
        value = p_points,
        height=150
    )
    
with col2:
    st.subheader("Set of D Distances")
    #d_distances = json.dumps(st.session_state.d_distances) if st.session_state.d_distances else ""
    d_distances = ", ".join(map(str, st.session_state.d_distances)) if st.session_state.d_distances else "" 
    d_text_area = st.text_area(
        label = "Generated D Distances",
        value = d_distances,
        height=150
    )


runner = CppRunner(CPP_EXE_PATH)
ui = Button(runner)

ui.render_generate_p_and_d(m, max_val)
ui.render_generate_d(p_text_area)