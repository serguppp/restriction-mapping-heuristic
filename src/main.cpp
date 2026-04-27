#include <iostream>
#include <vector>

#include "../include/generator.hpp"

int main() {
    int m = 5;
    int max_value = 25;
    std::cout << "Generated P: ";
    std::vector<int> p = generate_p(m, max_value);
    for (int i : p) {
        std::cout << i << " ";
    }
    std::cout << "\n";

    std::cout << "Generated D: ";
    std::vector<int> d = generate_d_from_p(p, 0);
    for (int i : d) {
        std::cout << i << " ";
    }
    std::cout << "\n";
    return 0;
}