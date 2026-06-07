import streamlit as st
import json
import time
import threading
import queue
import psutil
from components.config import Config
from components.runner import CppRunner
from components.types import States
from typing import IO
import signal

def map_text_to_list(text) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]

def map_list_to_string(list) -> str:
    return  ", ".join(map(str, list))

def dump_json(list: list) -> str:
    return json.dumps(list, separators=(",", ":"))

def enqueue_output(output: IO[str], q: queue.Queue) -> None:
    for line in iter(output.readline, ''):
        if line:
            q.put(line)
    output.close()

class Event():
    def __init__(self, runner) -> None:
        self.runner: CppRunner = runner

class SetDEvent(Event):
    def run(self, p_text_area:str, positive_errors: int, negative_errors: int) -> None:
        if not p_text_area.strip():
            st.warning("P vector is empty")
            return

        p_list_json = dump_json(map_text_to_list(p_text_area))

        stdout = self.runner.run_generate_d([p_list_json, str(positive_errors), str(negative_errors)])
        data = json.loads(stdout)

        if data["status"] == "success":
            st.session_state.d_distances = map_list_to_string(data["d_distances"])
            st.rerun()
    
class SetPDEvent(Event):
    def run(self, m, max_value:int, positive_errors: int, negative_errors: int) -> None:
        start = time.time()

        stdout = self.runner.run_generate_p_and_d([str(m), str(max_value), str(positive_errors), str(negative_errors)])
        data = json.loads(stdout)

        if data["status"] == "success":
            st.session_state.p_points = map_list_to_string(data["p_points"])
            st.session_state.d_distances = map_list_to_string(data["d_distances"])
            st.session_state.success_msg = f"Data generated successfully in {time.time() - start:.4f}s!"
            st.rerun()

class HeuristicEvents(Event):
    def run(self, p_text_area:str, d_text_area:str, population_size: int, mutation_rate: float, crossover_rate: float,
                              elite_rate: float, max_generations: int, tournament_size: int, status_text) -> None:
        if not p_text_area.strip() or not d_text_area.strip():
            st.warning("P or D vector is empty")
            return
        p_list_json = dump_json(map_text_to_list(p_text_area))
        d_list_json = dump_json(map_text_to_list(d_text_area))

        process = self.runner.run_heuristics([p_list_json, d_list_json, str(population_size), str(mutation_rate), str(crossover_rate), str(elite_rate), 
                                                str(max_generations), str(tournament_size)])
        

        st.session_state.run_state = States.RUNNING.value
        st.session_state.process = process
        st.session_state.log_buffer = ""
        st.session_state.stderr_queue = queue.Queue()

        thread = threading.Thread(
            target = enqueue_output,
            args=(process.stderr, st.session_state.stderr_queue)
        )
        
        thread.daemon = True
        thread.start()
        st.rerun()

    @staticmethod
    def pause() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            process.suspend()
            st.session_state.run_state = States.PAUSED.value
            st.session_state.success_msg = "Algorithm paused"
        st.rerun()

    @staticmethod
    def resume() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            process.resume()
            st.session_state.run_state = States.RUNNING.value
            st.session_state.success_msg = "Algorithm resumed"
        st.rerun()

    @staticmethod
    def stop() -> None:
        if st.session_state.process:
            process = psutil.Process(st.session_state.process.pid)
            if st.session_state.run_state == States.PAUSED.value:
                process.resume()
            process.send_signal(signal.SIGINT)
            st.session_state.process.wait(timeout=2)

            try:
                stdout_data, _ = st.session_state.process.communicate()
                if stdout_data:
                    data = json.loads(stdout_data)
                    if data["status"] == "success":
                        st.session_state.output_m_value = data["m_value"]
                        st.session_state.p_result = map_list_to_string(data["p_result"])
            except Exception:
                pass
            st.session_state.process = None
            st.session_state.log_buffer = ""
            st.session_state.success_msg = "Algorithm stopped"
        st.session_state.run_state = States.IDLE.value
        st.rerun()

class ResetParamsEvent():
    def __init__(self) -> None:
        pass
    def reset_params(self) -> None:
        config = Config.get()
        st.session_state.update(config)
