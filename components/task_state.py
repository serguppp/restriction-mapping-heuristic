from dataclasses import dataclass, field

import streamlit as st


@dataclass
class TaskState:
    # instance
    p_size: int = 10
    max_value: int = 100
    positive_errors: int = 0
    negative_errors: int = 0
    p_points: str = ""
    d_distances: str = ""

    # algorithm config
    population_size: int = 100
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    elite_rate: float = 0.1
    max_generations: int = 25
    tournament_size: int = 5
    max_time: float = 60.0

    # results
    p_result: str = ""
    m: int = 0
    current_time: float = 0.0
    generation: int = 0
    success_msg: str = ""

    results: list[dict[str, int | str | float]] = field(default_factory=list)

    @property
    def config_fields(self) -> list[str]:
        return [
            "population_size",
            "mutation_rate",
            "crossover_rate",
            "elite_rate",
            "max_generations",
            "tournament_size",
            "max_time",
        ]

    @property
    def instance_fields(self) -> list[str]:
        return [
            "p_size",
            "max_value",
            "positive_errors",
            "negative_errors",
        ]

    @property
    def all_fields(self) -> list[str]:
        return self.config_fields + self.instance_fields

    def reset(self, fields: list[str]) -> None:
        default = self.__class__()
        default_values = {key: getattr(default, key) for key in fields}
        self.__dict__.update(default_values)
        for f in fields:
            st.session_state[f"task_state.{f}"] = getattr(self, f)

    def reset_config(self) -> None:
        self.reset(self.config_fields)

    def reset_instance(self) -> None:
        self.reset(self.instance_fields)

    def set_results(
        self, generation: int, current_time: float, m: int, p_result: str
    ) -> None:
        self.generation = generation
        self.current_time = current_time
        self.m = m
        self.p_result = p_result
        self.results.append(
            {
                "generation": self.generation,
                "time": self.current_time,
                "m": self.m,
                "p_result": self.p_result,
            }
        )

    def reset_results(self) -> None:
        self.results = []
        self.generation = 0
        self.current_time = 0.0
        self.m = 0
        self.p_result = ""
        self.success_msg = ""
