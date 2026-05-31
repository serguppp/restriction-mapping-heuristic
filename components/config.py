class Config():
    @staticmethod
    def get():
        return {
            "m": 10,
            "max_value": 100,
            "population_size": 100,
            "mutation_rate": 0.05,
            "crossover_rate": 0.8,
            "elite_rate": 0.1,
            "max_generations": 100,
            "tournament_size": 5,
            "positive_errors": 0,
            "negative_errors": 0
        }