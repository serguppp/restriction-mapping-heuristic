import streamlit as st
import subprocess
import json
import time


def convert_text_to_list(text_area):
    return [int(x.strip()) for x in text_area.split(",") if x.strip()]

class Button():
    def __init__(self, runner):
        self.runner = runner
    
    def render_generate_p_and_d(self, m, max_val):
        if st.button("Generate P and D", type="primary"):
            start = time.time()

            process = self.runner.run_generate_p_and_d(m, max_val)
            data = json.loads(process.stdout)

            if data["status"] == "success":
                st.session_state.p_points = data["p_points"]
                st.session_state.d_distances = data["d_distances"]
                st.success(f"Done in {time.time() - start:.4f}s")
                st.rerun()

    def render_generate_d(self, p_text_area):
        if st.button("Generate D"):
            if not p_text_area.strip():
                st.warning("P vector is empty")
                return

            p_list = convert_text_to_list(p_text_area)
            process = self.runner.run_generate_d(p_list)
            data = json.loads(process.stdout)

            if data["status"] == "success":
                st.session_state.d_distances = data["d_distances"]
                st.rerun()

    def render_run_heuristics(self, p_text_area, d_text_area):
        if st.button("Run Algorithm"):
            p_list = convert_text_to_list(p_text_area)
            d_list = convert_text_to_list(d_text_area)
            process = self.runner.run_heuristics(p_list, d_list)
            data = json.loads(process.stdout)
        
            if data["status"] == "success":
                st.session_state.m_value = data["m_value"]
                st.session_state.p_result = data["p_result"]
                st.rerun()

