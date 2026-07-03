# Genetic Algorithm for the MIN SUPERSET PDP Problem

A multi-process web application designed to solve the **MIN SUPERSET PDP** problem (derived from DNA restriction mapping) using a hybrid (memetic) genetic algorithm.

---

## Problem Definition

The objective is to reconstruct the smallest possible set of DNA cleavage sites ($P$) based on a noisy multiset of measured distances ($D$).

*   **Input (Instance):** A multiset of positive integers $D = \{d_1, d_2, \dots, d_k\}$
*   **Solution:** A set of non-negative integers $P = \{p_1, p_2, \dots, p_m\}$ where the cardinality $m = |P|$ is **minimized**, such that:
    $$D \subseteq \{|p_i - p_j| : 1 \le i < j \le m\}$$

### Simple Example
Given the distances $D = \{2, 3, 5\}$, the optimal solution is $P = \{0, 2, 5\}$, because:
* $|0 - 2| = 2$
* $|0 - 5| = 5$
* $|2 - 5| = 3$

---

## System Architecture

The application utilizes a multi-process architecture to ensure that heavy background computations never freeze the user interface.
*   **Presentation Layer (Frontend):** Built with Python and Streamlit, featuring three tabs: *Instance*, *Heuristic*, and *Results*.
*   **Computation Layer (Backend):** A high-performance C++20 executable running as a separate background process. It communicates with the UI via `cout`/`cerr` streams using JSON formatting and is managed via the `psutil` library (supporting `SIGSTOP`, `SIGCONT`, and `SIGINT` signals).

---

## Application Overview

### 1. Instance Generator (`Instance`)
Generates test data using reverse engineering (uniform distribution sampling) and allows users to manually inject noise: negative errors (missing distances) and positive errors (false/redundant distances).

<img width="1402" height="418" alt="Instance Generator" src="https://github.com/user-attachments/assets/a1e1d864-7d30-46a8-b4d6-db4e44a8cbb4" />

### 2. Metaheuristic Panel (`Heuristic`)
Provides complete control over the genetic algorithm parameters while rendering real-time performance metrics and convergence charts ($m$ over time/generations).

<img width="1372" height="603" alt="Algorithm Parameters and Results" src="https://github.com/user-attachments/assets/f1e1d13c-a6e9-48f0-8078-a11b6b031a2a" />

### 3. Experiment History (`Results`)
Allows users to browse, filter, inspect, and re-visualize previously saved experiment configurations and results from JSON files.

<img width="1367" height="688" alt="Saved Experiments" src="https://github.com/user-attachments/assets/cb8c0d0a-d123-4f25-a3ed-6959868f2b77" />

---

## Metaheuristic Design & GA Modifications

The standard genetic algorithm was heavily customized to fit the domain knowledge of this combinatorial optimization problem:

1.  **Candidate Set $C$:** Search space is constrained strictly to points that can realistically be part of the solution based on $D$, capping the chromosome length at $|C| \le \max(D) + 1$.
2.  **Bit-Density Estimation:** Instead of initializing chromosomes randomly with a 50% bit probability (which causes memory explosion), the algorithm solves the quadratic equation $k = \frac{m(m-1)}{2}$ to estimate the ideal initial density of 1s.
3.  **Repair Function ( $O(n^3)$ ):** The core memetic component. Every offspring undergoes a two-phase heuristic adjustment to guarantee feasibility:
    *   *Greedy Phase:* Missing distances are resolved by inserting points from $C$ that yield the maximum possible coverage.
    *   *Removal Phase:* Redundant points are iteratively pruned as long as the remaining set fully covers $D$, strictly driving $m$ towards the minimum.
4.  **Operators:** Features tournament selection, two-point crossover (to preserve valuable gene blocks), and elitism.
5.  **Seeded Population (Super-individuals):** A configurable percentage of the initial population is generated greedily by applying the repair function to completely empty chromosomes, seeding the pool with strong solutions right from generation zero.

---

## Key Findings from Benchmark Tests

*   **Accuracy:** For small instances ($|P| \le 20$), the algorithm perfectly and consistently uncovers the global optimum (distance from optimum = $0.00$). For larger scales ($|P| \ge 30$), the exponential expansion of the search space causes standard random populations to get trapped in local minima.
*   **Noise Tolerance:** Highly **resilient to negative errors** because the repair function easily reconstructs missing links. It is significantly **more sensitive to positive errors**, as false distance data forces the repair operator to incorporate unneeded points to satisfy coverage constraints.
*   **Impact of Seeded Populations:** Seeding the pool with just 2% super-individuals massively improved convergence on large datasets. For $|P|=50, \max(D)=1000$, the average distance to the optimum dropped drastically from **37.97** down to **12.43**.
*   **Computational Performance:** The $O(n^3)$ repair function acts as the primary execution bottleneck. For the largest test cases ($|P|=50, \max(D)=1000$), a single generation takes roughly 3 seconds. However, seeding super-individuals reduces this time by ~20% because the repair operator processes much shorter phenotypic point arrays.

## Future Roadmap
*   Parallelize the point-validation and removal loops within the C++ repair operator using multi-threading.
*   Fix repair function's complexity.
*   Implement a full population reset mechanism (excluding the elite) when genetic stagnation is detected to help the algorithm escape local minima.
