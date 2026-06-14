#pragma once

#include <random>
#include <vector>

#include "../include/parameters.hpp"

struct Result {
    int generation;
    size_t p_size;
    std::vector<int> p_points;
    std::chrono::duration<double> time;
    std::string message;
};

struct Config {
    int POPULATION_SIZE;
    double MUTATION_RATE;
    double CROSSOVER_RATE;
    double ELITE_RATE;
    int MAX_GENERATIONS;
    int TOURNAMENT_SIZE;
    double SEEDED_POPULATION_RATE;
    std::chrono::duration<double> MAX_TIME;

    Config();
    Config(const Parameters& p);
};

struct Individual {
    std::vector<bool> chromosome;
    std::vector<int> P;
    double fitness;
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
    Individual create_seeded_individual();
    std::vector<int> decode_chromosome(const std::vector<bool>& chromosome);
    std::vector<bool> encode_chromosome(const std::vector<int>& P);
    Individual create_random_individual();
    std::vector<int> repair(std::vector<int> child_p);
    Individual select();
    std::pair<Individual, Individual> crossover(const Individual& p1, const Individual& p2);
    void mutate(Individual& ind);

   public:
    GeneticAlgorithm(Config& cfg, std::mt19937& g, const std::vector<int>& d);
    Result run();
};
