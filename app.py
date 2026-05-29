import streamlit as st
import subprocess
import json
import time
from components.button import Button
from components.runner import CppRunner

def map_list_to_string(string):
    return  ", ".join(map(str, string))

CPP_EXE_PATH = "./src/main"
# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="centered")
st.title("Restriction Mapping Heuristics")

if "p_points" not in st.session_state:
    st.session_state.p_points = ""
if "d_distances" not in st.session_state:
    st.session_state.d_distances = ""
if "m_value" not in st.session_state:
    st.session_state.m_value = ""
if "p_result" not in st.session_state:
    st.session_state.p_result = ""
if "success_msg" not in st.session_state:
    st.session_state.success_msg = ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Generated P Points")
    #p_points = json.dumps(st.session_state.p_points) if st.session_state.p_points else ""
    p_points = st.session_state.p_points if st.session_state.p_points else ""
    p_text_area = st.text_area(
        label = "Generated P Points",
        value = p_points,
        height=150
    )
    
with col2:
    st.subheader("Set of D Distances")
    #d_distances = json.dumps(st.session_state.d_distances) if st.session_state.d_distances else ""
    d_distances = st.session_state.d_distances if st.session_state.d_distances else "" 
    d_text_area = st.text_area(
        label = "Generated D Distances",
        value = d_distances,
        height=150
    )

if st.session_state.success_msg:
    st.success(st.session_state.success_msg)
    st.session_state.success_msg = ""
    
st.subheader("Algorithm Progress")
status_text = st.empty()

st.subheader("Results")

if st.session_state.m_value != "":
    st.metric(label="Found P Size (m)", value=st.session_state.m_value)
    
p_res = st.session_state.p_result if st.session_state.p_result else ""
st.text_area(
    label="Result P Points",
    value=p_res,
    height=150,
    disabled=True
)

runner = CppRunner(CPP_EXE_PATH)
button = Button(runner)

# UI
with st.sidebar:
    st.header("Input Parameters")
    m = st.slider("P size", min_value=5, max_value=100, value=10)
    max_val = st.number_input("Max Distance Value", min_value=10, max_value=1000, value=100)

    st.markdown("---")  
    st.header("Actions")

    button.render_generate_p_and_d(m, max_val)
    button.render_generate_d(st.session_state.p_points)
    button.render_run_heuristics(p_text_area, d_text_area, status_text)
