#include <algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <string>
#include <vector>

struct Config {
    const std::string TARGET = "CHRZASZCZ BRZMI W TRZCINIE W SZCZEBRZESZYNIE";
    const std::string GENES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ ";
    const int POPULATION_SIZE = 100;
    const double MUTATION_RATE = 0.05;
    const double CROSSOVER_RATE = 0.8;
    const double POPULATION_RATE = 0.1;
    const double TOURNAMENT_SIZE = 5;
};

struct Individual {
    std::string chromosome;
    int fitness;
};

class GeneticAlgorithm {
   private:
    Config config;
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

    char create_random_gene() { return config.GENES[random_int(0, static_cast<int>(config.GENES.size()) - 1)]; }

    int calculate_fitness(const std::string& chromosome) {
        int fitness = 0;
        for (size_t i = 0; i < config.TARGET.size(); i++) {
            if (chromosome[i] == config.TARGET[i]) {
                fitness++;
            }
        }
        return fitness;
    }

    Individual create_random_individual() {
        std::string chromosome;
        chromosome.reserve(config.TARGET.size());
        for (size_t i = 0; i < config.TARGET.size(); i++) {
            chromosome += create_random_gene();
        }
        return Individual{.chromosome = chromosome, .fitness = calculate_fitness(chromosome)};
    }

    Individual select_roulette() {
        double total_fitness = 0;
        for (const auto& i : population) {
            total_fitness += i.fitness;
        }

        if (total_fitness == 0) {
            return population[random_int(0, static_cast<int>(population.size()) - 1)];
        }

        double slice = random_double() * total_fitness;
        double sum = 0;
        for (const auto& i : population) {
            sum += i.fitness;
            if (sum >= slice) {
                return i;
            }
        }
        return population.back();
    }

    Individual reproduce(const Individual& parent1, const Individual& parent2) {
        std::string child_chromosome;
        child_chromosome.reserve(config.TARGET.size());

        bool do_crossover = random_double() < config.CROSSOVER_RATE;

        for (size_t i = 0; i < config.TARGET.size(); i++) {
            if (do_crossover) {
                child_chromosome += (random_double() < 0.5) ? parent1.chromosome[i] : parent2.chromosome[i];
            } else {
                child_chromosome += parent1.chromosome[i];
            }

            if (random_double() < config.MUTATION_RATE) {
                child_chromosome[i] = create_random_gene();
            }
        }

        return Individual{.chromosome = child_chromosome, .fitness = calculate_fitness(child_chromosome)};
    }

   public:
    GeneticAlgorithm(Config& cfg) : config(cfg), gen(std::random_device{}()) {
        for (int i = 0; i < config.POPULATION_SIZE; i++) {
            population.push_back(create_random_individual());
        }
    }

    void run() {
        int generation = 0;
        int max_fitness = static_cast<int>(config.TARGET.size());

        while (true) {
            std::ranges::sort(population.begin(), population.end(), [](const Individual& a, const Individual& b) { return a.fitness > b.fitness; });

            std::cout << "Pokolenie: " << generation << " | Najlepszy: " << population[0].chromosome << " | Fitness: " << population[0].fitness << "/" << max_fitness << "\n";

            if (population[0].fitness == max_fitness) {
                std::cout << "\nSukces! Cel osiagniety w pokoleniu " << generation << ".\n";
                break;
            }

            std::vector<Individual> next_generation;
            next_generation.reserve(config.POPULATION_SIZE);

            int elite_count = static_cast<int>(config.POPULATION_SIZE * config.POPULATION_RATE);
            for (int i = 0; i < elite_count; i++) {
                next_generation.push_back(population[i]);
            }

            while (next_generation.size() < static_cast<size_t>(config.POPULATION_SIZE)) {
                Individual parent1 = select_roulette();
                Individual parent2 = select_roulette();
                next_generation.push_back(reproduce(parent1, parent2));
            }

            population = std::move(next_generation);
            generation++;
        }
    }
};

int main() {
    Config config;
    GeneticAlgorithm ga(config);
    ga.run();

    return 0;
}