from dataclasses import asdict

import streamlit as st

from components.config import Config
from components.events import HeuristicEvents, SetDEvent, SetPDEvent

from components.runner import CppRunner
from components.types import States
from components.process import Process


def reset_params() -> None:
    st.session_state.update(asdict(Config()))  # type: ignore


CPP_EXE_PATH = "./src/main"
runner = CppRunner(CPP_EXE_PATH)

# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="wide")
st.header("Restriction Mapping Heuristics")
tab_config, tab_results = st.tabs(["Instance", "Results"])

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
if "output_generation_value" not in st.session_state:
    st.session_state.output_generation_value = ""
if "process" not in st.session_state:
    st.session_state.process = Process()

process = st.session_state.process


# I/O
with tab_config:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Input Parameters")
        col1_1, col2_2 = st.columns(2)
        with col1_1:
            m = st.number_input("P size", min_value=1, max_value=100, key="m")
            max_value = st.number_input(
                "Max Distance Value", min_value=1, max_value=1000, key="max_value"
            )
            population_size = st.number_input(
                "Population Size", min_value=1, max_value=1000, key="population_size"
            )
            mutation_rate = st.number_input(
                "Mutation Rate", min_value=0.01, max_value=1.0, key="mutation_rate"
            )
            positive_errors = st.number_input(
                "Positive Errors", min_value=0, key="positive_errors"
            )
        with col2_2:
            crossover_rate = st.number_input(
                "Crossover Rate", min_value=0.01, max_value=1.0, key="crossover_rate"
            )
            elite_rate = st.number_input(
                "Elite Rate", min_value=0.01, max_value=1.0, key="elite_rate"
            )
            max_generations = st.number_input(
                "Max Generations", min_value=1, max_value=10000, key="max_generations"
            )
            tournament_size = st.number_input(
                "Tournament Size", min_value=1, max_value=100, key="tournament_size"
            )
            negative_errors = st.number_input(
                "Negative Errors", min_value=0, key="negative_errors"
            )

    with col2:
        st.subheader("Generated P Points")
        p_points = st.session_state.p_points
        p_text_area = st.text_area(
            label="Generated P Points", value=p_points, height=150
        )

    with col3:
        st.subheader("Set of D Distances")
        d_distances = st.session_state.d_distances
        d_text_area = st.text_area(
            label="Generated D Distances", value=d_distances, height=150
        )

    with col2:
        st.button("Reset Params", on_click=reset_params)

        sb_col1, sb_col2, sb_col3 = st.columns([1.5, 1.5, 1])
        with sb_col1:
            if st.button("Set P,D", use_container_width=True):
                p_d_event = SetPDEvent(
                    runner,
                    m,
                    max_value,
                    st.session_state.positive_errors,
                    st.session_state.negative_errors,
                )
                p_d_event.run_and_proceed()
        with sb_col2:
            if st.button("Set D", use_container_width=True):
                d_event = SetDEvent(
                    runner,
                    st.session_state.p_points,
                    st.session_state.positive_errors,
                    st.session_state.negative_errors,
                )
                d_event.run_and_proceed()

with tab_results:
    col1, col2 = st.columns([1, 1])

    with col1:
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns(3)
        with ctrl_col1:
            if process.run_state == States.IDLE:
                if st.button("Run", type="primary", use_container_width=True):
                    heuristics_event = HeuristicEvents(
                        runner,
                        p_text_area,
                        d_text_area,
                        population_size,
                        mutation_rate,
                        crossover_rate,
                        elite_rate,
                        max_generations,
                        tournament_size,
                    )
                    heuristics_event.run_and_proceed(process)
            else:
                st.button("Run", disabled=True, use_container_width=True)

        with ctrl_col2:
            if process.run_state == States.RUNNING:
                if st.button("Pause", use_container_width=True):
                    process.pause()
            elif process.run_state == States.PAUSED:
                if st.button("Resume", use_container_width=True):
                    process.resume()
            else:
                st.button("Pause", disabled=True, use_container_width=True)

        with ctrl_col3:
            if process.run_state in (
                States.RUNNING,
                States.PAUSED,
            ):
                if st.button("Stop", type="primary", use_container_width=True):
                    process.stop()
            else:
                st.button("Stop", disabled=True, use_container_width=True)

        if st.session_state.success_msg:
            st.success(st.session_state.success_msg)
            st.session_state.success_msg = ""

    with col2:
        st.subheader("Results")
        st.metric(label="Generation", value=st.session_state.output_generation_value)
        st.metric(label="Found P Size (m)", value=st.session_state.output_m_value)
        st.text_area(
            label="Result P Points",
            value=st.session_state.p_result,
            height=150,
            disabled=True,
        )


process.update()
