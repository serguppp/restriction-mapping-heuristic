from __future__ import annotations

import json
import queue
import threading
from typing import IO, Any

import streamlit as st

from components.process import Process
from components.runner import CppRunner
from components.task_state import TaskState
from components.types import States, dump_json, map_list_to_string, map_text_to_list


def enqueue_output(output: IO[str], q: queue.Queue) -> None:
    for line in iter(output.readline, ""):
        if line:
            q.put(line)
    output.close()


class DEvent:
    @staticmethod
    def proceed_results(task_state: TaskState, data: dict[str, Any]) -> None:
        if data["status"] == "success":
            task_state.d_distances = map_list_to_string(data["d_distances"])
            st.rerun()

    @staticmethod
    def prepare_args(task_state: TaskState) -> list[str]:
        p_list_json = dump_json(map_text_to_list(task_state.p_points))
        return [
            p_list_json,
            str(task_state.positive_errors),
            str(task_state.negative_errors),
        ]

    @staticmethod
    def run_and_proceed(
        runner: CppRunner, task_state: TaskState, process: Process | None = None
    ) -> None:
        if not task_state.p_points:
            st.warning("P vector is empty")
            return
        try:
            args = DEvent.prepare_args(task_state)
            stdout = runner.run_generate_d(args)
            data = json.loads(stdout)
            DEvent.proceed_results(task_state, data)
        except Exception as e:
            st.error(f"Error generating D: {e}")


class PDEvent:
    @staticmethod
    def proceed_results(task_state: TaskState, data: dict[str, Any]) -> None:
        if data["status"] == "success":
            task_state.d_distances = map_list_to_string(data["d_distances"])
            task_state.p_points = map_list_to_string(data["p_points"])
            st.rerun()

    @staticmethod
    def prepare_args(task_state: TaskState) -> list[str]:
        args = [
            str(task_state.p_size),
            str(task_state.max_value),
            str(task_state.positive_errors),
            str(task_state.negative_errors),
        ]
        return args

    @staticmethod
    def run_and_proceed(
        runner: CppRunner, task_state: TaskState, process: Process | None = None
    ) -> None:
        try:
            args = PDEvent.prepare_args(task_state)
            stdout = runner.run_generate_p_and_d(args)
            data = json.loads(stdout)
            PDEvent.proceed_results(task_state, data)
        except Exception as e:
            st.error(f"Error generating P and D: {e}")


class HeuristicEvent:
    @staticmethod
    def prepare_args(task_state: TaskState) -> list[str]:
        p_list_json = dump_json(map_text_to_list(task_state.p_points))
        d_list_json = dump_json(map_text_to_list(task_state.d_distances))
        args = [
            p_list_json,
            d_list_json,
            str(task_state.population_size),
            str(task_state.mutation_rate),
            str(task_state.crossover_rate),
            str(task_state.elite_rate),
            str(task_state.max_generations),
            str(task_state.tournament_size),
            str(task_state.seeded_population_rate),
            str(task_state.max_time),
        ]
        return args

    @staticmethod
    def run_and_proceed(
        runner: CppRunner, task_state: TaskState, process: Process | None = None
    ) -> None:
        if not task_state.p_points or not task_state.d_distances:
            st.warning("P or D vector is empty")
            return

        try:
            task_state.reset_results()

            args = HeuristicEvent.prepare_args(task_state)
            subprocess = runner.run_heuristics(args)
            if process is None:
                raise Exception("No process manager provided")

            process.set(
                process=subprocess, run_state=States.RUNNING, queue=queue.Queue()
            )

            if process.process is not None and process.process.stderr is not None:
                thread = threading.Thread(
                    target=enqueue_output,
                    args=(process.process.stderr, process.queue),
                )

                thread.daemon = True
                thread.start()
                st.rerun()
        except Exception as e:
            st.error(f"Error starting heuristics: {e}")
