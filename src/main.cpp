#include <algorithm>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "../include/external/json.hpp"
#include "../include/generator.hpp"

using json = nlohmann::json;

enum class ExecutionMode { DEFAULT = 0, GENERATE_D = 1, RUN_HEURISTICS = 2 };

// 0 - Generowanie P i D
// 1 - Generowanie D na podstawie P
// 2 - Uruchomienie heurystyki
json process_flags(ExecutionMode flag, int p_size = 0, int max_value = 0, const std::vector<int>& p_vector = {}) {
    switch (flag) {
        case ExecutionMode::DEFAULT: {
            std::vector<int> p_points = generate_p(p_size, max_value);
            std::vector<int> d_distances = generate_d_from_p(p_points, 0);
            return json{{"status", "success"}, {"p_points", p_points}, {"d_distances", d_distances}};
        }
        case ExecutionMode::GENERATE_D: {
            std::vector<int> d_distances = generate_d_from_p(p_vector, 0);
            return json{{"status", "success"}, {"p_points", p_vector}, {"d_distances", d_distances}};
        }
        case ExecutionMode::RUN_HEURISTICS: {
            return json{{"status", "success"}, {"message", "Not implemented yet"}};
        }
        default:
            return json{{"status", "error"}, {"message", "Unknown execution mode"}};
    }
}

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << R"({"status": "error", "message": "Missing arguments <m> <max_value>"})" << "\n";
        return 1;
    }

    try {
        int flag_value = std::stoi(argv[1]);
        auto flag = static_cast<ExecutionMode>(flag_value);

        json output;
        if (flag == ExecutionMode::DEFAULT) {
            if (argc < 4) {
                std::cout << R"({"status": "error", "message": "Mode 0 requires: <p_size> <max_value>"})" << "\n";
                return 1;
            }
            int p_size = std::stoi(argv[2]);
            int max_val = std::stoi(argv[3]);
            output = process_flags(flag, p_size, max_val);

        } else if (flag == ExecutionMode::GENERATE_D) {
            if (argc < 3) {
                std::cout << R"({"status": "error", "message": "Mode 1 requires a JSON array string: '[1,2,3]'"})" << "\n";
                return 1;
            }
            std::vector<int> p_vector = json::parse(argv[2]).get<std::vector<int>>();
            output = process_flags(flag, 0, 0, p_vector);

        } else {
            output = process_flags(flag);
        }

        std::cout << output.dump() << "\n";

    } catch (const std::exception& e) {
        std::cout << R"({"status": "error", "message": "Exception in C++: "})" << e.what() << R"("})" << "\n";
        return 1;

    } catch (...) {
        std::cout << R"({"status": "error", "message": "Unknown critical error"})" << "\n";
        return 1;
    }

    return 0;
}