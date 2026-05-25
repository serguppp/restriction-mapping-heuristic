#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <set>
#include <string>
#include <vector>

// MIN SUPERSET PDB -  p = {p1, ..., pm} such that D = { |pi - pj| : 1 <= i < j <= m } and m is minimal
struct Config {
    const int POPULATION_SIZE = 100;
    const double MUTATION_RATE = 0.05;
    const double CROSSOVER_RATE = 0.8;
    const double ELITE_RATE = 0.1;
    const int MAX_GENERATIONS = 1000;
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

    int random_int(int start, int end) {
        std::uniform_int_distribution<> distr(start, end);
        return distr(gen);
    }

    double random_double() {
        std::uniform_real_distribution<> distr(0.0, 1.0);
        return distr(gen);
    }

    int calculate_fitness(const std::vector<int>& P) { return static_cast<int>(C.size() - P.size() + 1); }

    std::vector<int> set_candidates() {
        std::set<int> candidates;
        if (D.empty()) {
            return {};
        }

        int max_distance = *std::ranges::max_element(D.begin(), D.end());

        candidates.insert(0);
        candidates.insert(max_distance);

        for (int d : D) {
            candidates.insert(d);
            candidates.insert(max_distance - d);
        }

        return {candidates.begin(), candidates.end()};
    }

    std::vector<Individual> set_population() {
        std::vector<Individual> pop;
        pop.reserve(config.POPULATION_SIZE);
        for (int i = 0; i < config.POPULATION_SIZE; i++) {
            pop.push_back(create_random_individual());
        }
        return pop;
    }

    bool create_random_gene() { return random_double() < 0.5; }

    static std::vector<int> decode_chromosome(const std::vector<bool>& chromosome) {
        std::vector<int> p;
        for (size_t i = 0; i < chromosome.size(); i++) {
            if (chromosome[i]) {
                p.push_back(static_cast<int>(i));
            }
        }
        return p;
    }
    std::vector<bool> encode_chromosome(const std::vector<int>& P) {
        std::vector<bool> chromosome(C.size(), false);
        for (int p : P) {
            if (p >= 0 && p < static_cast<int>(chromosome.size())) {
                chromosome[p] = true;
            }
        }
        return chromosome;
    }

    std::vector<int> repair(const std::vector<int>& P) { return P; }

    Individual create_random_individual() {
        Individual ind;
        ind.chromosome.reserve(C.size());
        for (size_t i = 0; i < C.size(); i++) {
            ind.chromosome.push_back(create_random_gene());
        }
        ind.chromosome[0] = true;
        ind.chromosome[C.size() - 1] = true;
        ind.P = decode_chromosome(ind.chromosome);
    }

    Individual select_tournament() { return Individual{}; }

    std::pair<Individual, Individual> crossover() { return {Individual{}, Individual{}}; }

    void mutate(Individual& ind) {}

   public:
    GeneticAlgorithm(Config& cfg, std::mt19937& g, const std::vector<int>& d) : config(cfg), gen(g), D(d) {
        C = set_candidates();
        population = set_population();
    }

    void run() {
        int generation = 0;
        Individual best_individual = population[0];
        while (generation < config.MAX_GENERATIONS) {
            std::ranges::sort(population, [](const Individual& a, const Individual& b) { return a.fitness > b.fitness; });

            if (population[0].fitness > best_individual.fitness) {
                best_individual = population[0];
            }

            std::cout << "Generation " << generation << ": Best fitness = " << best_individual.fitness << ", P size = " << best_individual.P.size() << "\n";

            std::vector<Individual> new_population;
            new_population.reserve(config.POPULATION_SIZE);

            // these below move to separated functions
            int elite_count = static_cast<int>(config.ELITE_RATE * config.POPULATION_SIZE);
            for (int i = 0; i < elite_count; i++) {
                new_population.push_back(population[i]);
            }

            while (new_population.size() < config.POPULATION_SIZE) {
                Individual parent1 = select_tournament();
                Individual parent2 = select_tournament();

                Individual child1, child2;

                if (random_double() < config.CROSSOVER_RATE) {
                    auto [c1, c2] = crossover();
                    child1 = c1;
                    child2 = c2;
                }

                mutate(child1);
                mutate(child2);

                child1.P = repair(child1.P);
                child2.P = repair(child2.P);

                child1.chromosome = encode_chromosome(child1.P);
                child2.chromosome = encode_chromosome(child2.P);

                child1.fitness = calculate_fitness(child1.P);
                child2.fitness = calculate_fitness(child2.P);

                new_population.push_back(child1);
                if (new_population.size() < config.POPULATION_SIZE) {
                    new_population.push_back(child2);
                }
            }
            population = std::move(new_population);
            generation++;
        }
    }
};
