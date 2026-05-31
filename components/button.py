from numpy import negative
import streamlit as st
import json
import time
from components.config import Config
from components.runner import CppRunner

def map_text_to_list(text) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]

def map_list_to_string(list) -> str:
    return  ", ".join(map(str, list))

def dump_json(list: list) -> str:
    return json.dumps(list, separators=(",", ":"))

class RunnerButton():
    def __init__(self, runner) -> None:
        self.runner: CppRunner = runner
    
    def render_generate_p_and_d(self, m, max_value:int, positive_errors: int, negative_errors: int) -> None:
        if st.button("Set P,D", use_container_width=True):
            start = time.time()

            stdout = self.runner.run_generate_p_and_d([str(m), str(max_value), str(positive_errors), str(negative_errors)])
            data = json.loads(stdout)

            if data["status"] == "success":
                st.session_state.p_points = map_list_to_string(data["p_points"])
                st.session_state.d_distances = map_list_to_string(data["d_distances"])
                st.session_state.success_msg = f"Data generated successfully in {time.time() - start:.4f}s!"
                st.rerun()

    def render_generate_d(self, p_text_area:str, positive_errors: int, negative_errors: int) -> None:
        if st.button("Set D", use_container_width=True):
            if not p_text_area.strip():
                st.warning("P vector is empty")
                return

            p_list_json = dump_json(map_text_to_list(p_text_area))

            stdout = self.runner.run_generate_d([p_list_json, str(positive_errors), str(negative_errors)])
            data = json.loads(stdout)

            if data["status"] == "success":
                st.session_state.d_distances = map_list_to_string(data["d_distances"])
                st.rerun()

    def render_run_heuristics(self, p_text_area:str, d_text_area:str, population_size: int, mutation_rate: float, crossover_rate: float,
                              elite_rate: float, max_generations: int, tournament_size: int, status_text) -> None:
        if st.button("Run", type="primary"):
            if not p_text_area.strip() or not d_text_area.strip():
                st.warning("P or D vector is empty")
                return
            p_list_json = dump_json(map_text_to_list(p_text_area))
            d_list_json = dump_json(map_text_to_list(d_text_area))

            process = self.runner.run_heuristics([p_list_json, d_list_json, str(population_size), str(mutation_rate), str(crossover_rate), str(elite_rate), 
                                                 str(max_generations), str(tournament_size)])
            
            if process.stderr:
                for line in process.stderr:
                    if line:
                        status_text.code(line.strip(), language="text")

            stdout_data, _ = process.communicate()

            if stdout_data:
                data = json.loads(stdout_data)
                
                if data["status"] == "success":
                    st.session_state.output_m_value = data["m_value"]
                    st.session_state.p_result = map_list_to_string(data["p_result"])
                    st.session_state.success_msg = "Algorithm finished successfully!"
                    st.rerun()

class Button():
    def __init__(self) -> None:
        pass
    def _reset_params(self) -> None:
        config = Config.get()
        st.session_state.update(config)
    def render_reset_params(self) -> None:
        st.button("Reset Params", on_click=self._reset_params)
