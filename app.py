import streamlit as st
from components.events import DEvent, HeuristicEvent, PDEvent
from components.process import Process
from components.runner import CppRunner
from components.task_state import TaskState
from components.types import States
from components.results import get_results_df

CPP_EXE_PATH = "./src/main"
runner = CppRunner(CPP_EXE_PATH)

if "task_state" not in st.session_state:
    st.session_state.task_state = TaskState()
task_state: TaskState = st.session_state.task_state

if "process" not in st.session_state:
    st.session_state.process = Process(task_state=task_state)
process: Process = st.session_state.process

for field in task_state.config_fields:
    st.session_state.setdefault(f"task_state.{field}", getattr(task_state, field))


def reset_config() -> None:
    task_state.reset_config()
    for field in task_state.config_fields:
        st.session_state[f"task_state.{field}"] = getattr(task_state, field)


# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristics", layout="wide")
st.header("Restriction Mapping Heuristics")
tab_config, tab_results = st.tabs(["Instance", "Results"])

# I/O
with tab_config:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Input Parameters")
        col1_1, col2_2 = st.columns(2)
        with col1_1:
            task_state.p_size = st.number_input(
                "P size",
                min_value=1,
                max_value=100,
                key="task_state.p_size",
            )
            task_state.max_value = st.number_input(
                "Max Distance Value",
                min_value=1,
                max_value=1000,
                key="task_state.max_value",
            )
            task_state.population_size = st.number_input(
                "Population Size",
                min_value=1,
                max_value=1000,
                key="task_state.population_size",
            )
            task_state.mutation_rate = st.number_input(
                "Mutation Rate",
                min_value=0.01,
                max_value=1.0,
                key="task_state.mutation_rate",
            )
            task_state.positive_errors = st.number_input(
                "Positive Errors", min_value=0, key="task_state.positive_errors"
            )

        with col2_2:
            task_state.crossover_rate = st.number_input(
                "Crossover Rate",
                min_value=0.01,
                max_value=1.0,
                key="task_state.crossover_rate",
            )
            task_state.elite_rate = st.number_input(
                "Elite Rate", min_value=0.01, max_value=1.0, key="task_state.elite_rate"
            )
            task_state.max_generations = st.number_input(
                "Max Generations",
                min_value=1,
                max_value=10000,
                key="task_state.max_generations",
            )
            task_state.tournament_size = st.number_input(
                "Tournament Size",
                min_value=1,
                max_value=100,
                key="task_state.tournament_size",
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
        st.button("Reset Params", on_click=reset_config)

        sb_col1, sb_col2, sb_col3 = st.columns([1.5, 1.5, 1])
        with sb_col1:
            if st.button("Set P,D", use_container_width=True):
                PDEvent.run_and_proceed(runner=runner, task_state=task_state)

        with sb_col2:
            if st.button("Set D", use_container_width=True):
                DEvent.run_and_proceed(runner=runner, task_state=task_state)


with tab_results:
    col1, col2, col3= st.columns([0.2, 0.3, 0.5])

    with col1:
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
        st.subheader("Results")
        st.metric(label="Generation", value=task_state.generation)
        st.metric(label="Found P Size (m)", value=task_state.m)
        st.text_area(
            label="Result P Points",
            value=task_state.p_result,
            height=150,
            width=300,
            disabled=True,
        )

    with col3:
        if task_state.results:
            st.line_chart(
                get_results_df(task_state.p_size, task_state.results),
                x="generation",
                y=["Target value (P size)", "Current value (m)"],
                width='stretch'
            )
process.update()
