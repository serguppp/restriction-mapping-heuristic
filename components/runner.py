import streamlit as st
import subprocess


class CppRunner:
    def __init__(self, exe_path):
        self.exe_path = exe_path

    def run_generate_p_and_d(self, m:str, max_value:str):
        return subprocess.run(
            [self.exe_path, "0", m, max_value], 
            capture_output=True, 
            text=True, 
            check=True
        )
    
    def run_generate_d(self, args:list[str]):
        return subprocess.run(
            [self.exe_path, "1", *args],
            capture_output=True,
            text=True,
            check=True
        )
    
    def run_heuristics(self, args:list[str]):
        return subprocess.Popen(
            [self.exe_path, "2", *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 
        )