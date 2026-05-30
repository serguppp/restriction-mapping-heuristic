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
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="wide")
st.title("Restriction Mapping Heuristics")

# P and D I/O
if "p_points" not in st.session_state:
    st.session_state.p_points = ""
if "d_distances" not in st.session_state:
    st.session_state.d_distances = ""
if "p_result" not in st.session_state:
    st.session_state.p_result = ""

# Algorithm Parameters
if "m_value" not in st.session_state:
    st.session_state.m_value = ""
if "population_size" not in st.session_state:
    st.session_state.population_size = ""
if "mutation_rate" not in st.session_state:
    st.session_state.mutation_rate = ""
if "crossover_rate" not in st.session_state:
    st.session_state.crossover_rate = ""
if "elite_rate" not in st.session_state:
    st.session_state.elite_rate = ""
if "max_generations" not in st.session_state:
    st.session_state.max_generations = ""
if "tournament_size" not in st.session_state:
    st.session_state.tournament_size = ""
if "success_msg" not in st.session_state:
    st.session_state.success_msg = ""

col1, col2, col3 = st.columns([1,1,1])

with col2:
    st.subheader("Generated P Points")
    p_points = st.session_state.p_points
    p_text_area = st.text_area(
        label = "Generated P Points",
        value = p_points,
        height=150
    )
    
with col3:
    st.subheader("Set of D Distances")
    d_distances = st.session_state.d_distances
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
with col1:
    st.subheader("Input Parameters")
    col1_1, col2_2 = st.columns(2)
    with col1_1:
        m = st.number_input("P size", min_value=1, max_value=100, value=10)
        max_value = st.number_input("Max Distance Value", min_value=1, max_value=1000, value=100)
        population_size = st.number_input("Population Size", min_value=1, max_value=1000, value=100)
        mutation_rate = st.number_input("Mutation Rate", min_value=0.01, max_value=1.0, value=0.05)
    with col2_2:
        crossover_rate = st.number_input("Crossover Rate", min_value=0.01, max_value=1.0, value=0.8)
        elite_rate = st.number_input("Elite Rate", min_value=0.01, max_value=1.0, value=0.1)
        max_generations = st.number_input("Max Generations", min_value=1, max_value=10000, value=100)
        tournament_size = st.number_input("Tournament Size", min_value=1, max_value=100, value=5)
    
    st.header("Actions")

    sb_col1, sb_col2, sb_col3 = st.columns([1.5,1.5,1])
    with sb_col1:
        button.render_generate_p_and_d(m, max_value)
    with sb_col2:
        button.render_generate_d(st.session_state.p_points)
    with sb_col3:
        button.render_run_heuristics(p_text_area, d_text_area, population_size, mutation_rate, crossover_rate, elite_rate, max_generations, tournament_size, status_text)

