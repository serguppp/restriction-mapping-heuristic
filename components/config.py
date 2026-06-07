import streamlit as st
from dataclasses import dataclass, asdict


@dataclass
class Config:
    m: int = 10
    max_value: int = 100
    population_size: int = 100
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    elite_rate: float = 0.1
    max_generations: int = 100
    tournament_size: int = 5
    positive_errors: int = 0
    negative_errors: int = 0

    @classmethod
    def update(cls) -> None:
        default_config = asdict(cls())

        for key, value in default_config.items():
            if key not in st.session_state:
                st.session_state[key] = value
