#pragma once
#include <string>
#include <vector>

enum class ExecutionMode { DEFAULT = 0, GENERATE_D = 1, RUN_HEURISTICS = 2 };

struct Parameters {
    ExecutionMode flag;
    int m;
    int max_value;
    std::vector<int> p_vector;
    std::vector<int> d_vector;
    std::string population_size;
    std::string mutation_rate;
    std::string crossover_rate;
    std::string elite_rate;
    std::string max_generations;
    std::string tournament_size;
};