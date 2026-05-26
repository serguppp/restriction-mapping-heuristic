#pragma once

#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// MIN SUPERSET PDB - p = {p1, ..., pm} such that D = { |pi - pj| : 1 <= i < j <= m } and m is minimal
struct Config {
    const int POPULATION_SIZE = 100;
    const double MUTATION_RATE = 0.05;
    const double CROSSOVER_RATE = 0.8;
    const double ELITE_RATE = 0.1;
    const int MAX_GENERATIONS = 1000;
    const int TOURNAMENT_SIZE = 5;
};

struct Individual {
    std::vector<bool> chromosome;
    std::vector<int> P;
    double fitness = 0.0;
};

class GeneticAlgorithm {
   private:
    Config config;
    std::vector<int> D;
    std::vector<int> C;
    std::vector<Individual> population;
    std::mt19937 gen;

    int random_int(int start, int end);
    double random_double();
    int calculate_fitness(const std::vector<int>& P);
    std::vector<int> set_candidates();
    std::vector<Individual> set_population();
    bool create_random_gene();
    std::vector<int> decode_chromosome(const std::vector<bool>& chromosome);
    std::vector<bool> encode_chromosome(const std::vector<int>& P);
    Individual create_random_individual();
    std::vector<int> repair(std::vector<int> child_p);
    Individual select();
    std::pair<Individual, Individual> crossover(const Individual& p1, const Individual& p2);
    void mutate(Individual& ind);

   public:
    GeneticAlgorithm(Config& cfg, std::mt19937& g, const std::vector<int>& d);
    std::pair<int, std::vector<int>> run();
};
