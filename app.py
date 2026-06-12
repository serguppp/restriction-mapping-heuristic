import streamlit as st

from components.events import DEvent, HeuristicEvent, PDEvent
from components.process import Process
from components.results import get_results_df
from components.runner import CppRunner
from components.task_state import TaskState
from components.types import States

CPP_EXE_PATH = "./src/main"
runner = CppRunner(CPP_EXE_PATH)


if "task_state" not in st.session_state:
    st.session_state.task_state = TaskState()
task_state: TaskState = st.session_state.task_state

if "process" not in st.session_state:
    st.session_state.process = Process(task_state=task_state)
process: Process = st.session_state.process

for field in task_state.all_fields:
    st.session_state.setdefault(f"task_state.{field}", getattr(task_state, field))

# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristic Algorithm", layout="wide")
st.header("Restriction Mapping Heuristic Algorithm")
tab_config, tab_results = st.tabs(["Instance", "Results"])

# I/O
with tab_config:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Instance Parameters")
        col_input_1, col_input_2 = st.columns(2)
        with col_input_1:
            task_state.p_size = st.number_input(
                "P size",
                min_value=1,
                max_value=100,
                key="task_state.p_size",
            )
            task_state.positive_errors = st.number_input(
                "Positive Errors", min_value=0, key="task_state.positive_errors"
            )

        with col_input_2:
            task_state.max_value = st.number_input(
                "Max Distance Value",
                min_value=1,
                max_value=1000,
                key="task_state.max_value",
            )
            task_state.negative_errors = st.number_input(
                "Negative Errors", min_value=0, key="task_state.negative_errors"
            )

    with col2:
        st.subheader("Generated P Points")
        st.text_area(label="Generated P Points", value=task_state.p_points, height=150)

    with col3:
        st.subheader("Set of D Distances")
        st.text_area(
            label="Generated D Distances", value=task_state.d_distances, height=150
        )

    with col2:
        st.button("Reset Params", on_click=task_state.reset_instance)

        col_reset_1, col_reset_2 = st.columns([1.5, 1.5])
        with col_reset_1:
            if st.button("Set P,D", use_container_width=True):
                PDEvent.run_and_proceed(runner=runner, task_state=task_state)

        with col_reset_2:
            if st.button("Set D", use_container_width=True):
                DEvent.run_and_proceed(runner=runner, task_state=task_state)


with tab_results:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Algorithm Parameters")

        col_results_1, col_results_2 = st.columns(2)
        with col_results_1:
            task_state.population_size = st.number_input(
                "Population Size",
                min_value=1,
                max_value=10000,
                key="task_state.population_size",
            )
            task_state.mutation_rate = st.number_input(
                "Mutation Rate",
                min_value=0.01,
                max_value=1.0,
                key="task_state.mutation_rate",
            )
            task_state.crossover_rate = st.number_input(
                "Crossover Rate",
                min_value=0.01,
                max_value=1.0,
                key="task_state.crossover_rate",
            )

        with col_results_2:
            task_state.tournament_size = st.number_input(
                "Tournament Size",
                min_value=1,
                max_value=100,
                key="task_state.tournament_size",
            )
            task_state.max_generations = st.number_input(
                "Max Generations",
                min_value=1,
                max_value=10000,
                key="task_state.max_generations",
            )
            task_state.max_time = st.number_input(
                "Max Time (seconds)",
                min_value=1.0,
                max_value=3600.0,
                key="task_state.max_time",
            )

        col_results_3, col_results_4 = st.columns(2, vertical_alignment="bottom")
        with col_results_3:
            task_state.elite_rate = st.number_input(
                "Elite Rate", min_value=0.01, max_value=1.0, key="task_state.elite_rate"
            )
        with col_results_4:
            st.button(
                "Reset Config",
                on_click=task_state.reset_config,
                use_container_width=True,
            )

        if process.run_state == States.IDLE:
            if st.button("Run", type="primary", use_container_width=True):
                HeuristicEvent.run_and_proceed(
                    runner=runner, task_state=task_state, process=process
                )
        else:
            st.button("Run", disabled=True, use_container_width=True)

        if process.run_state == States.RUNNING:
            if st.button("Pause", use_container_width=True):
                process.pause()
        elif process.run_state == States.PAUSED:
            if st.button("Resume", use_container_width=True):
                process.resume()
        else:
            st.button("Pause", disabled=True, use_container_width=True)

        if process.run_state in (
            States.RUNNING,
            States.PAUSED,
        ):
            if st.button("Stop", type="primary", use_container_width=True):
                process.stop()
        else:
            st.button("Stop", disabled=True, use_container_width=True)

        if task_state.success_msg:
            st.success(task_state.success_msg)
            task_state.success_msg = ""

    with col2:
        st.subheader("Heuristic")

        col_results_1, col_results_2, col_results_3 = st.columns([1, 1, 1])
        with col_results_1:
            st.metric(label="Time (seconds)", value=task_state.current_time)

        with col_results_2:
            st.metric(label="Generation", value=task_state.generation)

        with col_results_3:
            st.metric(label="Found P Size (m)", value=task_state.m)

        st.text_area(
            label="Result P Points",
            value=task_state.p_result,
            height=150,
            width=500,
            disabled=True,
        )
    with col3:
        if task_state.results:
            st.line_chart(
                get_results_df(task_state.p_size, task_state.results),
                x="generation",
                y=["Target value (P size)", "Current value (m)"],
                width="stretch",
            )

            st.line_chart(
                get_results_df(task_state.p_size, task_state.results),
                x="time",
                y=["Target value (P size)", "Current value (m)"],
                width="stretch",
            )
process.update()
