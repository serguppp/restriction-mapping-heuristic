#include <algorithm>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "../include/external/json.hpp"
#include "../include/generator.hpp"
#include "../include/heuristics.hpp"
#include "../include/parameters.hpp"

using json = nlohmann::json;

// 0 - Generowanie P i D
// 1 - Generowanie D na podstawie P
// 2 - Uruchomienie heurystyki

Parameters parse_arguments(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << R"({"status": "error", "message": "Missing arguments: <mode>"})" << "\n";
        throw std::runtime_error("Invalid arguments");
    }

    Parameters params;

    int flag_value = std::stoi(argv[1]);
    params.flag = static_cast<ExecutionMode>(flag_value);

    switch (params.flag) {
        case ExecutionMode::DEFAULT: {
            if (argc < 6) {
                std::cerr << R"({"status": "error", "message": "Mode 0 requires parameters: <m:str> <max_value:str> <positive_errors:int> <negative_errors:int>"})" << "\n";
                throw std::runtime_error("Invalid arguments");
            }
            params.m = std::stoi(argv[2]);
            params.max_value = std::stoi(argv[3]);
            params.positive_errors = std::stoi(argv[4]);
            params.negative_errors = std::stoi(argv[5]);
            break;
        }
        case ExecutionMode::GENERATE_D: {
            if (argc < 5) {
                std::cerr << R"({"status": "error", "message": "Mode 1 requires parameters: <mode:str> <p_list_json:str> <positive_errors:int> <negative_errors:int>})" << "\n";
                throw std::runtime_error("Invalid arguments");
            }
            params.p_vector = json::parse(argv[2]).get<std::vector<int>>();
            params.positive_errors = std::stoi(argv[3]);
            params.negative_errors = std::stoi(argv[4]);
            break;
        }

        case ExecutionMode::RUN_HEURISTICS: {
            if (argc < 10) {
                std::cerr
                    << R"({"status": "error", "message": "Mode 2 requires parameters: <mode:str> <p_list_json:str> <d_list_json:str> <population_size:str>, <mutation_rate:str>, <crossover_rate:str>, <elite_rate:str>, <max_generations:str>, <tournament_size:str>"})"
                    << "\n";
                throw std::runtime_error("Invalid arguments");
            }
            params.flag = ExecutionMode::RUN_HEURISTICS;
            params.p_vector = json::parse(argv[2]).get<std::vector<int>>();
            params.d_vector = json::parse(argv[3]).get<std::vector<int>>();
            params.population_size = std::stoi(argv[4]);
            params.mutation_rate = std::stod(argv[5]);
            params.crossover_rate = std::stod(argv[6]);
            params.elite_rate = std::stod(argv[7]);
            params.max_generations = std::stoi(argv[8]);
            params.tournament_size = std::stoi(argv[9]);
            break;
        }
        default: {
            std::cerr << R"({"status": "error", "message": "Unknown execution mode"})" << "\n";
            throw std::runtime_error("Invalid arguments");
        }
    }
    return params;
}

json process_flags(const Parameters& params) {
    switch (params.flag) {
        case ExecutionMode::DEFAULT: {
            auto p_vector = generate_p(params.m, params.max_value);
            auto d_vector = generate_d_from_p(p_vector, params.positive_errors, params.negative_errors);
            return json{{"status", "success"}, {"p_points", p_vector}, {"d_distances", d_vector}};
        }
        case ExecutionMode::GENERATE_D: {
            auto d_vector = generate_d_from_p(params.p_vector, params.positive_errors, params.negative_errors);
            return json{{"status", "success"}, {"p_points", params.p_vector}, {"d_distances", d_vector}};
        }
        case ExecutionMode::RUN_HEURISTICS: {
            Config cfg(params);
            GeneticAlgorithm ga(cfg, get_gen(), params.d_vector);
            std::pair<int, std::vector<int>> result = ga.run();
            return json{{"status", "success"}, {"m_value", result.first}, {"p_result", result.second}};
        }
        default:
            return json{{"status", "error"}, {"message", "Unknown execution mode"}};
    }
}

int main(int argc, char** argv) {
    try {
        Parameters params = parse_arguments(argc, argv);
        auto output = process_flags(params);

        std::cout << output.dump() << "\n";

    } catch (const std::exception& e) {
        std::cerr << R"({"status": "error", "message": "Exception in C++: "})" << e.what() << R"("})" << "\n";
    }

    return 0;
}