import math
import random
import matplotlib.pyplot as plt
import statistics
import os
from math import gamma, sin, pi

class TSPInstance:
    def __init__(self, coords):
        self.coords = coords
        self.n = len(coords)
        self.dist_matrix = self.compute_distance_matrix()

    def compute_distance_matrix(self):
        matrix = [[0.0] * self.n for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    x1, y1 = self.coords[i]
                    x2, y2 = self.coords[j]
                    matrix[i][j] = math.hypot(x1 - x2, y1 - y2)
                else:
                    matrix[i][j] = float('inf')
        return matrix

class LevyACO:
    def __init__(self, tsp, ants=20, iterations=1000, alpha=1.0, beta=3.0, rho=0.1,
                 levy_beta=1.5, levy_threshold=0.8, altering_ratio=9.5, elitist_weight=5,
                 seed=None):

        self.tsp = tsp
        self.ants = ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.n = tsp.n
        self.pheromone = [[1.0] * self.n for _ in range(self.n)]
        self.eta = [[(1.0 / tsp.dist_matrix[i][j]) if i != j and tsp.dist_matrix[i][j] != float('inf') else 0.0
                     for j in range(self.n)] for i in range(self.n)]
        self.best_path = None
        self.best_cost = float("inf")
        self.levy_beta = levy_beta
        self.levy_threshold = levy_threshold
        self.altering_ratio = altering_ratio / 100.0
        self.elitist_weight = elitist_weight
        if seed is not None:
            random.seed(seed)

        # inicialização do feromônio
        init_tau = 1.0 / (self.n * statistics.mean([min(row) for row in tsp.dist_matrix if min(row) != float('inf')]))
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    self.pheromone[i][j] = init_tau

    def mantegna_levy(self):
        beta = self.levy_beta
        num = gamma(1 + beta) * sin(pi * beta / 2.0)
        den = gamma((1 + beta) / 2.0) * beta * 2 ** ((beta - 1) / 2.0)
        sigma_u = (num / den) ** (1.0 / beta)
        u = random.gauss(0, sigma_u)
        v = random.gauss(0, 1)
        return u / (abs(v) ** (1.0 / beta) + 1e-16)

    def select_next_probabilistic(self, current, visited):
        probs = []
        total = 0.0
        for j in range(self.n):
            if j not in visited:
                tau = (self.pheromone[current][j] ** self.alpha)
                eta = (self.eta[current][j] ** self.beta)
                p = tau * eta
                probs.append((j, p))
                total += p

        if total <= 0:
            choices = [j for j in range(self.n) if j not in visited]
            return random.choice(choices)

        r = random.random() * total
        accum = 0.0
        for node, prob in probs:
            accum += prob
            if accum >= r:
                return node
        return probs[-1][0]

    def nearest_to_point_unvisited(self, target_point, visited):
        best = None
        best_dist = float("inf")
        tx, ty = target_point
        for j in range(self.n):
            if j not in visited:
                xj, yj = self.tsp.coords[j]
                d = math.hypot(tx - xj, ty - yj)
                if d < best_dist:
                    best_dist = d
                    best = j
        return best if best is not None else random.choice([j for j in range(self.n) if j not in visited])

    def construct_solution(self, use_levy_global, best_global):
        start = random.randrange(self.n)
        path = [start]
        visited = set(path)

        for _ in range(self.n - 1):
            current = path[-1]
            if use_levy_global and best_global is not None and random.random() < self.altering_ratio:
                cx, cy = self.tsp.coords[current]
                levy_step = abs(self.mantegna_levy())
                tx = cx + levy_step
                ty = cy + levy_step
                next_node = self.nearest_to_point_unvisited((tx, ty), visited)
            else:
                next_node = self.select_next_probabilistic(current, visited)

            path.append(next_node)
            visited.add(next_node)

        return path

    def path_cost(self, path):
        return sum(self.tsp.dist_matrix[path[i]][path[(i + 1) % self.n]] for i in range(self.n))

    def update_pheromone(self, paths, costs):
        for i in range(self.n):
            for j in range(self.n):
                self.pheromone[i][j] *= (1.0 - self.rho)
                if self.pheromone[i][j] < 1e-12:
                    self.pheromone[i][j] = 1e-12

        for path, cost in zip(paths, costs):
            deposit = 1.0 / (cost)
            for i in range(self.n):
                a, b = path[i], path[(i + 1) % self.n]
                self.pheromone[a][b] += deposit

        if self.best_path is not None:
            global_deposit = self.elitist_weight * (1.0 / (self.best_cost))
            for i in range(self.n):
                a, b = self.best_path[i], self.best_path[(i + 1) % self.n]
                self.pheromone[a][b] += global_deposit

    def run(self, verbose=False):
        for it in range(self.iterations):
            paths = []
            costs = []
            use_levy = (random.random() < self.levy_threshold)
            ref = self.best_path

            for _ in range(self.ants):
                path = self.construct_solution(use_levy, ref)
                cost = self.path_cost(path)

                paths.append(path)
                costs.append(cost)

                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_path = path
                    if verbose:
                        print(f"[it {it}] Novo melhor custo: {round(self.best_cost,2)}")

            self.update_pheromone(paths, costs)

        return self.best_path, self.best_cost


def load_tsp(filename):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Arquivo não encontrado: {filename}")

    coords = []
    with open(filename, "r") as f:
        reading = False
        for line in f:
            line = line.strip()
            if line.upper() == "NODE_COORD_SECTION":
                reading = True
                continue
            if not reading:
                continue
            if line.startswith("EOF"):
                break
            parts = line.split()
            if len(parts) >= 3:
                coords.append((float(parts[-2]), float(parts[-1])))
    
    if len(coords) == 0:
        raise ValueError("Nenhuma coordenada encontrada no arquivo TSP!")

    return TSPInstance(coords)


def plot_path(tsp, path, filename="levy_solution.png"):
    xs, ys = zip(*[tsp.coords[i] for i in path + [path[0]]])
    plt.figure(figsize=(8, 6))
    plt.plot(xs, ys, marker="o")
    plt.title("Levy-ACO - Melhor Solução")
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    tsp = load_tsp("TSP/berlin52.tsp")

    aco = LevyACO(tsp, ants=30, iterations=500, alpha=1.0, beta=3.0, rho=0.1,
                  levy_beta=1.5, levy_threshold=0.8, altering_ratio=9.5,
                  elitist_weight=5, seed=42)

    best_path, best_cost = aco.run(verbose=True)

    print("\nBest Path:", best_path)
    print("Best Cost:", round(best_cost, 2))

    plot_path(tsp, best_path)
    print("Imagem salva: levy_solution.png")
