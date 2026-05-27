import streamlit as st
import subprocess
import json
import time


def map_text_to_list(text):
    return [int(x.strip()) for x in text.split(",") if x.strip()]

def map_list_to_string(list):
    return  ", ".join(map(str, list))

class Button():
    def __init__(self, runner):
        self.runner = runner
    
    def render_generate_p_and_d(self, m, max_val:str):
        if st.button("Generate P and D", type="primary"):
            start = time.time()

            process = self.runner.run_generate_p_and_d(m, max_val)
            data = json.loads(process.stdout)

            if data["status"] == "success":
                st.session_state.p_points = map_list_to_string(data["p_points"])
                st.session_state.d_distances = map_list_to_string(data["d_distances"])
                st.session_state.success_msg = f"Data generated successfully in {time.time() - start:.4f}s!"
                st.rerun()

    def render_generate_d(self, p_text_area:str):
        if st.button("Generate D"):
            if not p_text_area.strip():
                st.warning("P vector is empty")
                return

            p_list = map_text_to_list(p_text_area)
            process = self.runner.run_generate_d(p_list)
            data = json.loads(process.stdout)

            if data["status"] == "success":
                st.session_state.d_distances = map_list_to_string(data["d_distances"])
                st.rerun()

    def render_run_heuristics(self, p_text_area:str, d_text_area:str, status_text):
        if st.button("Run Algorithm"):
            p_list = map_text_to_list(p_text_area)
            d_list = map_text_to_list(d_text_area)

            process = self.runner.run_heuristics(p_list, d_list)
            while True:
                line = process.stderr.readline()
                if not line and process.poll() is not None:
                    break 
                if line:
                    status_text.code(line.strip(), language="text")

            data = json.loads(process.stdout.read())
                
            if data["status"] == "success":
                st.session_state.m_value = data["m_value"]
                st.session_state.p_result = map_list_to_string(data["p_result"])
                st.session_state.success_msg = "Algorithm finished successfully!"
                st.rerun()
 

