#include <algorithm>
#include <iostream>
#include <random>
#include <string>
#include <vector>

#include "../include/external/json.hpp"
#include "../include/generator.hpp"

using json = nlohmann::json;

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << R"({"status": "error", "message": "Missing arguments <m> <max_value>"})" << "\n";
        return 1;
    }

    try {
        int m = std::stoi(argv[1]);
        int max_val = std::stoi(argv[2]);

        std::vector<int> p = generate_p(m, max_val);
        std::vector<int> d = generate_d_from_p(p, 0);

        json j = {{"status", "success"}, {"m", m}, {"max_value", max_val}, {"p_points", p}, {"d_distances", d}};

        std::cout << j.dump() << "\n";

    } catch (const std::exception& e) {
        std::cout << R"({"status": "error", "message": "Exception in C++: "})" << e.what() << R"("})" << "\n";
        return 1;

    } catch (...) {
        std::cout << R"({"status": "error", "message": "Unknown critical error"})" << "\n";
        return 1;
    }

    return 0;
}