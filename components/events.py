from abc import ABC, abstractmethod
import streamlit as st
import json
import threading
import queue
from components.processes import ProcessManager
from components.runner import CppRunner
from components.types import States, map_list_to_string, map_text_to_list, dump_json
from typing import IO, Any


def enqueue_output(output: IO[str], q: queue.Queue) -> None:
    for line in iter(output.readline, ''):
        if line:
            q.put(line)
    output.close()

class Event(ABC):
    def __init__(self, runner: CppRunner) -> None:
        self.runner = runner

    @abstractmethod
    def prepare_args(self) -> list[str]:
        pass

    @abstractmethod
    def proceed_results(self, data: dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    def run_and_proceed(self) -> None:
        pass
    
class SetDEvent(Event):
    def __init__(self, runner: CppRunner, p_points: str, positive_errors: int, negative_errors: int) -> None:
        super().__init__(runner)
        self.p_points = p_points.strip()
        self.positive_errors = positive_errors
        self.negative_errors = negative_errors
    
    def proceed_results(self, data: dict[str, Any]) -> None:
        if data["status"] == "success":
            st.session_state.d_distances = map_list_to_string(data["d_distances"])
            st.rerun()

    def prepare_args(self) -> list[str]:
        p_list_json = dump_json(map_text_to_list(self.p_points))
        return [p_list_json, str(self.positive_errors), str(self.negative_errors)]
    
    def run_and_proceed(self) -> None:
        if not self.p_points:
            st.warning("P vector is empty")
            return
        try:
            args = self.prepare_args()
            stdout = self.runner.run_generate_d(args)
            data = json.loads(stdout)
            self.proceed_results(data)
        except Exception as e:
            st.error(f"Error generating D: {e}")

    
class SetPDEvent(Event):
    def __init__(self, runner: CppRunner, m: int, max_value:int, positive_errors: int, negative_errors: int) -> None:
        super().__init__(runner)
        self.m = m
        self.max_value = max_value
        self.positive_errors = positive_errors
        self.negative_errors = negative_errors

    def proceed_results(self, data: dict[str, Any]) -> None:
        if data["status"] == "success":
            st.session_state.d_distances = map_list_to_string(data["d_distances"])
            st.session_state.p_points = map_list_to_string(data["p_points"])
            st.rerun()

    def prepare_args(self) -> list[str]:
        args = [str(self.m), str(self.max_value), str(self.positive_errors), str(self.negative_errors)]
        return args

    def run_and_proceed(self) -> None:
        try:
            args = self.prepare_args()
            stdout = self.runner.run_generate_p_and_d(args)
            data = json.loads(stdout)
            self.proceed_results(data)
        except Exception as e:
            st.error(f"Error generating P and D: {e}")

class HeuristicEvents(Event):
    def __init__(self, runner: CppRunner, p_text_area: str, d_text_area: str, population_size: int, 
                 mutation_rate: float, crossover_rate: float, elite_rate: float, 
                 max_generations: int, tournament_size: int) -> None:
        super().__init__(runner)
        self.p_text_area = p_text_area.strip()
        self.d_text_area = d_text_area.strip()
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_rate = elite_rate
        self.max_generations = max_generations
        self.tournament_size = tournament_size

    def proceed_results(self, data: dict[str, Any]) -> None:
        pass

    def prepare_args(self) -> list[str]:
        p_list_json = dump_json(map_text_to_list(self.p_text_area))
        d_list_json = dump_json(map_text_to_list(self.d_text_area))
        args = [p_list_json, d_list_json, str(self.population_size), str(self.mutation_rate), str(self.crossover_rate), str(self.elite_rate), 
                                                str(self.max_generations), str(self.tournament_size)]
        return args

    def run_and_proceed(self) -> None:
        if not self.p_text_area or not self.d_text_area:
            st.warning("P or D vector is empty")
            return
        try:
            args = self.prepare_args()
            process = self.runner.run_heuristics(args)
            
            st.session_state.run_state = States.RUNNING.value
            st.session_state.process = process
            st.session_state.stderr_queue = queue.Queue()

            thread = threading.Thread(
                target = enqueue_output,
                args=(process.stderr, st.session_state.stderr_queue)
            )
            
            thread.daemon = True
            thread.start()
        except Exception as e:
            st.error(f"Error starting heuristics: {e}")

            
