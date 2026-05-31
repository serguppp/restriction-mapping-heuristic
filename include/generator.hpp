#pragma once

#include <algorithm>
#include <iostream>
#include <random>
#include <ranges>
#include <vector>

std::vector<int> generate_p(int m, int max_value);
std::vector<int> generate_d_from_p(const std::vector<int>& p, int positive_errors, int negative_errors);
std::mt19937& get_gen();