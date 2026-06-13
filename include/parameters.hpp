#pragma once
#include <chrono>
#include <vector>

enum class ExecutionMode { DEFAULT = 0, GENERATE_D = 1, RUN_HEURISTICS = 2 };

struct Parameters {
    ExecutionMode flag;
    int m;
    int max_value;
    std::vector<int> p_vector;
    std::vector<int> d_vector;
    int population_size;
    double mutation_rate;
    double crossover_rate;
    double elite_rate;
    int max_generations;
    int tournament_size;
    double seeded_population_rate;
    std::chrono::duration<double> max_time;
    int positive_errors;
    int negative_errors;
};