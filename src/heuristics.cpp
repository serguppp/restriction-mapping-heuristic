#include "../include/heuristics.hpp"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <csignal>
#include <iostream>
#include <set>

extern std::atomic<bool> stop;

GeneticAlgorithm::GeneticAlgorithm(Config& cfg, std::mt19937& g, const std::vector<int>& d) : config(cfg), gen(g), D(d) {
    std::ranges::sort(D);
    C = set_candidates();
    population = set_population();
}

int GeneticAlgorithm::random_int(int start, int end) {
    std::uniform_int_distribution<> distr(start, end);
    return distr(gen);
}

double GeneticAlgorithm::random_double() {
    std::uniform_real_distribution<> distr(0.0, 1.0);
    return distr(gen);
}

int GeneticAlgorithm::calculate_fitness(const std::vector<int>& P) { return static_cast<int>(C.size() - P.size() + 1); }

std::vector<int> GeneticAlgorithm::set_candidates() {
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

bool GeneticAlgorithm::create_random_gene() { return random_double() < 0.5; }

std::vector<Individual> GeneticAlgorithm::set_population() {
    std::vector<Individual> population;
    population.reserve(config.POPULATION_SIZE);

    int seed_count = static_cast<int>(0.10 * config.POPULATION_SIZE);
    seed_count = std::max(seed_count, 1);

    for (int i = 0; i < seed_count; i++) {
        population.push_back(create_seeded_individual());
    }

    for (int i = seed_count; i < config.POPULATION_SIZE; i++) {
        population.push_back(create_random_individual());
    }
    std::ranges::sort(population, [](const Individual& a, const Individual& b) { return a.fitness > b.fitness; });
    return population;
}

std::vector<int> GeneticAlgorithm::decode_chromosome(const std::vector<bool>& chromosome) {
    std::vector<int> p;
    for (size_t i = 0; i < chromosome.size(); i++) {
        if (chromosome[i]) {
            p.push_back(C[i]);
        }
    }
    return p;
}
std::vector<bool> GeneticAlgorithm::encode_chromosome(const std::vector<int>& P) {
    std::vector<bool> chromosome(C.size(), false);
    for (int p : P) {
        auto it = std::ranges::find(C, p);
        if (it != C.end()) {
            chromosome[std::ranges::distance(C.begin(), it)] = true;
        }
    }

    chromosome[0] = true;
    chromosome.back() = true;
    return chromosome;
}

Individual GeneticAlgorithm::create_seeded_individual() {
    Individual ind;
    ind.chromosome.resize(C.size(), false);
    ind.chromosome[0] = true;
    ind.chromosome.back() = true;

    ind.P = decode_chromosome(ind.chromosome);
    ind.P = repair(ind.P);
    ind.chromosome = encode_chromosome(ind.P);
    ind.fitness = calculate_fitness(ind.P);
    return ind;
}

Individual GeneticAlgorithm::create_random_individual() {
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

std::vector<int> GeneticAlgorithm::repair(std::vector<int> child_p) {
    std::ranges::sort(child_p);
    int max_distance = *std::ranges::max_element(D.begin(), D.end());

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

        int d = missing_d_values.back();
        int d_max = max_distance - d;

        int cover_count_d = 0;
        int cover_count_d_max = 0;

        for (int p : child_p) {
            int dist_d = std::abs(p - d);
            int dist_d_max = std::abs(p - d_max);
            if (std::ranges::find(missing_d_values, dist_d) != missing_d_values.end()) {
                cover_count_d++;
            }
            if (std::ranges::find(missing_d_values, dist_d_max) != missing_d_values.end()) {
                cover_count_d_max++;
            }
        }

        int best = cover_count_d > cover_count_d_max ? d : d_max;
        child_p.push_back(best);
        std::ranges::sort(child_p);
    }

    for (size_t i = 1; i < child_p.size();) {
        std::vector<int> temp_p = child_p;
        temp_p.erase(temp_p.begin() + static_cast<int>(i));

        std::vector<int> temp_d;
        temp_d.reserve(temp_p.size() * (temp_p.size() - 1) / 2);
        for (size_t i = 0; i < temp_p.size(); i++) {
            for (size_t j = i + 1; j < temp_p.size(); j++) {
                int diff = std::abs(temp_p[i] - temp_p[j]);
                temp_d.push_back(diff);
            }
        }

        std::ranges::sort(temp_d);
        std::vector<int> missing_d_values;
        std::ranges::set_difference(D, temp_d, std::back_inserter(missing_d_values));

        if (missing_d_values.empty()) {
            child_p.erase(child_p.begin() + static_cast<int>(i));
        } else {
            i++;
        }
    }

    return child_p;
}

Individual GeneticAlgorithm::select() {
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

std::pair<Individual, Individual> GeneticAlgorithm::crossover(const Individual& p1, const Individual& p2) {
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

void GeneticAlgorithm::mutate(Individual& ind) {
    for (size_t i = 1; i < C.size() - 1; i++) {
        if (random_double() < config.MUTATION_RATE) {
            ind.chromosome[i] = !ind.chromosome[i];
        }
    }
}

Result GeneticAlgorithm::run() {
    auto start_time = std::chrono::steady_clock::now();
    std::chrono::duration<double> elapsed_time;
    int generation = 0;
    int generations_without_progress = 0;
    Individual best_individual = population[0];

    std::string message;
    while (true) {
        if (stop) {
            message = "Algorithm stopped by user";
            break;
        }

        auto current_time = std::chrono::steady_clock::now();
        elapsed_time = current_time - start_time;
        std::cerr << "Generation " << generation << ", Time: " << elapsed_time.count() << ": Fitness = " << best_individual.fitness << ", P size = " << best_individual.P.size() << ", Best P = ";
        for (size_t i = 0; i < best_individual.P.size(); i++) {
            std::cerr << best_individual.P[i] << (i == best_individual.P.size() - 1 ? "" : ",");
        }
        std::cerr << "\n";

        if (elapsed_time >= config.MAX_TIME) {
            message = "Algorithm stopped by time limit";
            break;
        }

        if (generations_without_progress >= config.MAX_GENERATIONS) {
            message = "Algorithm stopped by generations limit";
            break;
        }
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

        std::ranges::sort(population, [](const Individual& a, const Individual& b) { return a.fitness > b.fitness; });

        if (population[0].fitness > best_individual.fitness) {
            best_individual = population[0];
            generations_without_progress = 0;
        } else {
            generations_without_progress++;
        }

        generation++;
    }

    return {.generation = generation, .p_size = best_individual.P.size(), .p_points = best_individual.P, .time = elapsed_time, .message = message};
}
