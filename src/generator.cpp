#include "../include/generator.hpp"

std::mt19937& get_gen() {
    static std::mt19937 gen(std::random_device{}());
    return gen;
}

std::vector<int> generate_p(int m, int max_value) {
    if (max_value < m) {
        throw std::invalid_argument("max_value must be greater than or equal to m to ensure unique values in P.");
    }

    std::uniform_int_distribution<> dis(1, max_value);
    std::vector<int> p;
    p.reserve(m);

    p.push_back(0);
    while (p.size() < m) {
        int value = dis(get_gen());
        if (std::ranges::find(p.begin(), p.end(), value) == p.end()) {
            p.push_back(value);
        }
    }

    std::ranges::sort(p.begin(), p.end());
    return p;
}

std::vector<int> generate_d_from_p(const std::vector<int>& p, int positive_errors = 0, int negative_errors = 0) {
    int m = static_cast<int>(p.size());
    int k = (m * (m - 1)) / 2;
    std::vector<int> d;
    d.reserve(k + positive_errors);
    for (int i = 0; i < m; i++) {
        for (int j = i + 1; j < m; j++) {
            int diff = std::abs(p[i] - p[j]);
            d.push_back(diff);
        }
    }

    if (negative_errors > 0) {
        negative_errors = std::ranges::min(negative_errors, static_cast<int>(d.size()));
        std::shuffle(d.begin(), d.end(), get_gen());
        d.resize(d.size() - negative_errors);
    }

    if (positive_errors > 0) {
        int max_range = std::ranges::max(p);
        std::uniform_int_distribution<> dis(1, max_range);
        for (int i = 0; i < positive_errors; i++) {
            d.push_back(dis(get_gen()));
        }
    }

    std::shuffle(d.begin(), d.end(), get_gen());
    return d;
}
