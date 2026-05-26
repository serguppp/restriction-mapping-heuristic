import streamlit as st
import subprocess
import json


def dump_json(list):
    return json.dumps(list, separators=(",", ":"))

class CppRunner:
    def __init__(self, exe_path):
        self.exe_path = exe_path

    def run_generate_p_and_d(self, m, max_val):
        return subprocess.run(
            [self.exe_path, "0", str(m), str(max_val)], 
            capture_output=True, 
            text=True, 
            check=True
        )
    
    def run_generate_d(self, p_list):
        return subprocess.run(
            [self.exe_path, "1", dump_json(p_list)],
            capture_output=True,
            text=True,
            check=True
        )
    
    def run_heuristics(self, p_list, d_list):
        return subprocess.Popen(
            [self.exe_path, "2", dump_json(p_list), dump_json(d_list)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 
        )