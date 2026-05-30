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
    
    def run_generate_d(self, p_list_json: str):
        return subprocess.run(
            [self.exe_path, "1", p_list_json],
            capture_output=True,
            text=True,
            check=True
        )
    
    def run_heuristics(self, p_list_json: str, d_list_json: str, population_size: str, mutation_rate: str, crossover_rate: str,
                        elite_rate: str, max_generations: str, tournament_size: str):
        return subprocess.Popen(
            [self.exe_path, "2", p_list_json, d_list_json, population_size, mutation_rate, crossover_rate, elite_rate, max_generations, tournament_size],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1 
        )