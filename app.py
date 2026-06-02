import streamlit as st
from components.event import ResetParamsEvent, SetDEvent, SetPDEvent, RunHeuristicsEvent
from components.runner import CppRunner
from components.config import Config
from collections import Counter

CPP_EXE_PATH = "./src/main"

# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="wide")
st.header("Restriction Mapping Heuristics")
tab_config, tab_results = st.tabs(["Instance", "Results"])

# I/O
with tab_config:
    Config.update()

    if "p_points" not in st.session_state:
        st.session_state.p_points = ""
    if "d_distances" not in st.session_state:
        st.session_state.d_distances = ""
    if "p_result" not in st.session_state:
        st.session_state.p_result = ""
    if "output_m_value" not in st.session_state:
        st.session_state.output_m_value = ""
    if "success_msg" not in st.session_state:
        st.session_state.success_msg = ""

    # UI 
    col1, col2, col3 = st.columns([1,1,1])


    with col1:
        st.subheader("Input Parameters")
        col1_1, col2_2 = st.columns(2)
        with col1_1:
            m = st.number_input("P size", min_value=1, max_value=100, key = "m")
            max_value = st.number_input("Max Distance Value", min_value=1, max_value=1000, key = "max_value")
            population_size = st.number_input("Population Size", min_value=1, max_value=1000,  key = "population_size")
            mutation_rate = st.number_input("Mutation Rate", min_value=0.01, max_value=1.0, key = "mutation_rate")
            positive_errors = st.number_input("Positive Errors", min_value = 0, key = "positive_errors")
        with col2_2:
            crossover_rate = st.number_input("Crossover Rate", min_value=0.01, max_value=1.0, key = "crossover_rate")
            elite_rate = st.number_input("Elite Rate", min_value=0.01, max_value=1.0, key = "elite_rate")
            max_generations = st.number_input("Max Generations", min_value=1, max_value=10000, key = "max_generations")
            tournament_size = st.number_input("Tournament Size", min_value=1, max_value=100, key = "tournament_size")
            negative_errors = st.number_input("Negative Errors", min_value = 0, key = "negative_errors")

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

    runner = CppRunner(CPP_EXE_PATH)

    with col2:
        reset_params_event = ResetParamsEvent()
        st.button("Reset Params", on_click=reset_params_event.reset_params)

        sb_col1, sb_col2, sb_col3 = st.columns([1.5,1.5,1])
        with sb_col1:
            if st.button("Set P,D", use_container_width=True):
                p_d_event = SetPDEvent(runner)
                p_d_event.run(m, max_value, st.session_state.positive_errors, st.session_state.negative_errors)
        with sb_col2:
            if st.button("Set D", use_container_width=True):
                d_event = SetDEvent(runner)
                d_event.run(st.session_state.p_points, st.session_state.positive_errors, st.session_state.negative_errors)

with tab_results:
    col1, col2 = st.columns([1,1])

    with col1:
        st.subheader("Algorithm Progress")
        status_text = st.empty()

    with col2:
        st.subheader("Results")

        if st.session_state.output_m_value != "":
            st.metric(label="Found P Size (m)", value=st.session_state.output_m_value)
            
        p_res = st.session_state.p_result if st.session_state.p_result else ""
        st.text_area(
            label="Result P Points",
            value=p_res,
            height=150,
            disabled=True
        )

    if st.button("Run", type="primary"):
        h_event = RunHeuristicsEvent(runner)
        h_event.run(p_text_area, d_text_area, population_size, mutation_rate, crossover_rate, elite_rate, max_generations, tournament_size, status_text)

    if st.session_state.success_msg: 
        st.success(st.session_state.success_msg)
        st.session_state.success_msg = ""

