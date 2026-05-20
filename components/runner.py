import streamlit as st
import subprocess
import json

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
            [self.exe_path, "1", json.dumps(p_list, separators=(",", ":"))],
            capture_output=True,
            text=True,
            check=True
        )