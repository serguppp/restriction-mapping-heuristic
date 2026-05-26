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

    std::vector<int> decode_chromosome(const std::vector<bool>& chromosome) {
        std::vector<int> p;
        for (size_t i = 0; i < chromosome.size(); i++) {
            if (chromosome[i]) {
                p.push_back(C[i]);
            }
        }
        return p;
    }
    std::vector<bool> encode_chromosome(const std::vector<int>& P) {
        std::vector<bool> chromosome(C.size(), false);
        for (unsigned int p : P) {
            auto it = std::ranges::find(C, p);
            if (it != C.end()) {
                chromosome[std::ranges::distance(C.begin(), it)] = true;
            }
        }

        chromosome[0] = true;
        chromosome.back() = true;
        return chromosome;
    }
    Individual create_random_individual() {
        Individual ind;
        ind.chromosome.reserve(C.size());
        for (size_t i = 0; i < C.size(); i++) {
            ind.chromosome.push_back(create_random_gene());
        }
        ind.chromosome[0] = true;
        ind.chromosome.back() = true;

        ind.P = decode_chromosome(ind.chromosome);
        ind.P = repair(ind.P);
        ind.chromosome = encode_chromosome(ind.P);
        ind.fitness = calculate_fitness(ind.P);
        return ind;
    }

    std::vector<int> repair(std::vector<int> child_p) {
        std::ranges::sort(child_p);
        while (true) {
            std::vector<int> child_d;
            for (size_t i = 0; i < child_p.size(); i++) {
                for (size_t j = i + 1; j < child_p.size(); j++) {
                    child_d.push_back(std::abs(child_p[i] - child_p[j]));
                }
            }
            std::ranges::sort(child_d);
            std::vector<int> missing_d_values;
            std::ranges::set_difference(D, child_d, std::back_inserter(missing_d_values));

            if (missing_d_values.empty()) {
                break;
            }

            // greedy repiar
            int missing_distance = missing_d_values.back();
            child_p.push_back(missing_distance);
        }

        return child_p;
    }

    Individual select() {
        Individual best_ind;
        best_ind.fitness = -1.0;

        for (int i = 0; i < config.TOURNAMENT_SIZE; i++) {
            int random_id = random_int(0, static_cast<int>(population.size() - 1));
            if (population[random_id].fitness > best_ind.fitness) {
                best_ind = population[random_id];
            }
        }
        return best_ind;
    }

    std::pair<Individual, Individual> crossover(const Individual& p1, const Individual& p2) {
        Individual c1;
        Individual c2;

        c1.chromosome.resize(C.size());
        c2.chromosome.resize(C.size());

        for (size_t i = 0; i < C.size(); i++) {
            if (random_double() < 0.5) {
                c1.chromosome[i] = p1.chromosome[i];
                c2.chromosome[i] = p2.chromosome[i];
            } else {
                c1.chromosome[i] = p2.chromosome[i];
                c2.chromosome[i] = p1.chromosome[i];
            }
        }
        return {c1, c2};
    }

    void mutate(Individual& ind) {
        for (size_t i = 1; i < C.size() - 1; i++) {
            if (random_double() < config.MUTATION_RATE) {
                ind.chromosome[i] = !ind.chromosome[i];
            }
        }
    }

   public:
    GeneticAlgorithm(Config& cfg, std::mt19937& g, const std::vector<int>& d) : config(cfg), gen(g), D(d) {
        C = set_candidates();
        population = set_population();
        std::ranges::sort(D);
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
                Individual parent1 = select();
                Individual parent2 = select();

                Individual child1 = parent1;
                Individual child2 = parent2;

                if (random_double() < config.CROSSOVER_RATE) {
                    auto [c1, c2] = crossover(parent1, parent2);
                    child1 = c1;
                    child2 = c2;
                }

                mutate(child1);
                mutate(child2);

                child1.P = decode_chromosome(child1.chromosome);
                child2.P = decode_chromosome(child2.chromosome);

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
