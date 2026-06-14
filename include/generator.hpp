#pragma once

#include <random>
#include <vector>

std::vector<int> generate_p(int m, int d_size);
std::vector<int> generate_d_from_p(const std::vector<int>& p, int positive_errors, int negative_errors);
std::mt19937& get_gen();