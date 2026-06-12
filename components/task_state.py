from dataclasses import dataclass, field

@dataclass
class TaskState:
    # config
    p_size: int = 10
    max_value: int = 100
    population_size: int = 100
    mutation_rate: float = 0.05
    crossover_rate: float = 0.8
    elite_rate: float = 0.1
    max_generations: int = 100
    tournament_size: int = 5
    positive_errors: int = 0
    negative_errors: int = 0

    # instance
    p_points: str = ""
    d_distances: str = ""

    # results
    p_result: str = ""
    m: int = 0
    generation: int = 0
    success_msg: str = ""

    results: list[dict[str, int | str]] = field(default_factory=list)

    @property
    def config_fields(self) -> list[str]:
        return [
            "p_size",
            "max_value",
            "population_size",
            "mutation_rate",
            "positive_errors",
            "crossover_rate",
            "elite_rate",
            "max_generations",
            "tournament_size",
            "negative_errors",
        ]

    def reset_config(self) -> None:
        default = self.__class__()
        default_values = {key: getattr(default, key) for key in self.config_fields}
        self.__dict__.update(default_values)

    def reset_results(self) -> None:
        self.results = []