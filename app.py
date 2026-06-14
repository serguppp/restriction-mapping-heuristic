import streamlit as st

from components.constants import CPP_EXE_PATH
from components.events import DEvent, HeuristicEvent, PDEvent
from components.process import Process
from components.results import (
    delete_results,
    get_results_df,
    read_results,
    save_results,
)
from components.runner import CppRunner
from components.task_state import TaskState
from components.types import States

runner = CppRunner(CPP_EXE_PATH)

if "task_state" not in st.session_state:
    st.session_state.task_state = TaskState()
task_state: TaskState = st.session_state.task_state

if "process" not in st.session_state:
    st.session_state.process = Process(task_state=task_state)
process: Process = st.session_state.process

if "selected_experiment" not in st.session_state:
    st.session_state.selected_experiment = None


for field in task_state.all_fields:
    st.session_state.setdefault(f"task_state.{field}", getattr(task_state, field))

# Page settings
st.set_page_config(page_title="Restriction Mapping Heuristic Algorithm", layout="wide")
st.header("Restriction Mapping Heuristic Algorithm")
tab_config, tab_heuristic, tab_results = st.tabs(["Instance", "Heuristic", "Results"])

# I/O
with tab_config:
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Instance Parameters")
        col_input_1, col_input_2 = st.columns(2)
        with col_input_1:
            task_state.p_size = st.number_input(
                "P Size",
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
                max_value=100000,
                key="task_state.max_value",
            )
            task_state.negative_errors = st.number_input(
                "Negative Errors", min_value=0, key="task_state.negative_errors"
            )

    with col2:
        st.subheader("Generated P Points")
        task_state.p_points = st.text_area(
            label="Generated P Points", value=task_state.p_points, height=150
        )

    with col3:
        st.subheader("Set of D Distances")
        task_state.d_distances = st.text_area(
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


with tab_heuristic:
    col1, col2, col3 = st.columns(3)

    with col1:
        col_header_1, col_header_2 = st.columns(2, vertical_alignment="center")
        with col_header_1:
            st.subheader("Algorithm Parameters")
        with col_header_2:
            st.button(
                "Reset Config",
                on_click=task_state.reset_config,
                use_container_width=True,
            )

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
                min_value=0.001,
                max_value=1.0,
                key="task_state.mutation_rate",
            )
            task_state.crossover_rate = st.number_input(
                "Crossover Rate",
                min_value=0.001,
                max_value=1.0,
                key="task_state.crossover_rate",
            )
            task_state.elite_rate = st.number_input(
                "Elite Rate", min_value=0.01, max_value=1.0, key="task_state.elite_rate"
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
            task_state.seeded_population_rate = st.number_input(
                "Seeded Population Rate",
                min_value=0.0,
                max_value=1.0,
                key="task_state.seeded_population_rate",
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

    with col2:
        st.subheader("Results")

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

        if task_state.success_msg:
            st.success(task_state.success_msg)
            task_state.success_msg = ""

        if st.button("Save", use_container_width=True):
            save_results(task_state)

    with col3:
        if task_state.results:
            st.line_chart(
                get_results_df(task_state.p_size, task_state.results),
                x="Generation",
                y=["Target value (P size)", "Current value (m)"],
                width="stretch",
            )

            st.line_chart(
                get_results_df(task_state.p_size, task_state.results),
                x="Time (seconds)",
                y=["Target value (P size)", "Current value (m)"],
                width="stretch",
            )

with tab_results:
    saved_experiments = read_results()

    if not saved_experiments:
        st.info("No saved experiments found.")
    else:
        col_list, col_details = st.columns([1.2, 1.8])

        with col_list:
            st.subheader("Experiment List")

            col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([2.5, 1, 1, 1, 0.8])
            col_h1.caption("**File Name**")
            col_h2.caption("**P size**")
            col_h3.caption("**m**")
            col_h4.caption("**Action**")
            col_h5.caption("**Del**")
            st.divider()

            for file_name, exp_state in saved_experiments:
                col_f, col_p, col_m, col_btn, col_del = st.columns(
                    [2.5, 1, 1, 1, 0.8], vertical_alignment="center"
                )

                display_name = file_name.replace("results_", "").replace(".json", "")
                col_f.text(display_name)
                col_p.text(str(exp_state.p_size))
                col_m.text(str(exp_state.m))

                if col_btn.button(
                    "SHOW", key=f"show_{file_name}", use_container_width=True
                ):
                    st.session_state.selected_experiment = (file_name, exp_state)
                    st.rerun()

                if col_del.button("❌", key=f"del_{file_name}"):
                    delete_results(file_name)
                    if (
                        st.session_state.selected_experiment
                        and st.session_state.selected_experiment[0] == file_name
                    ):
                        st.session_state.selected_experiment = None
                    st.toast(f"Deleted {display_name}")
                    st.rerun()

        with col_details:
            st.subheader("Experiment Details")

            if st.session_state.selected_experiment is not None:
                selected_name, selected_state = st.session_state.selected_experiment

                st.info(f"Viewing: `{selected_name}`")

                exp_col1, exp_col2 = st.columns(2)
                with exp_col1:
                    st.subheader("Instance Parameters:")
                    st.json(
                        {
                            "P Size": selected_state.p_size,
                            "Max Distance Value": selected_state.max_value,
                            "Positive Errors": selected_state.positive_errors,
                            "Negative Errors": selected_state.negative_errors,
                        }
                    )
                with exp_col2:
                    st.subheader("Algorithm Parameters:")
                    st.json(
                        {
                            "Population Size": selected_state.population_size,
                            "Mutation Rate": selected_state.mutation_rate,
                            "Crossover Rate": selected_state.crossover_rate,
                            "Elite Rate": selected_state.elite_rate,
                            "Tournament Size": selected_state.tournament_size,
                            "Seeded Population Rate": selected_state.seeded_population_rate,
                            "Max Generations": selected_state.max_generations,
                            "Max Time": selected_state.max_time,
                        }
                    )

                if selected_state.results:
                    df_selected = get_results_df(
                        selected_state.p_size, selected_state.results
                    )

                    st.line_chart(
                        df_selected,
                        x="Generation",
                        y=["Target value (P size)", "Current value (m)"],
                        height=300,
                    )
                else:
                    st.warning("No iteration history stored inside this file.")

process.update()
