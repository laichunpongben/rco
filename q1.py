#!/usr/bin/python3

from __future__ import print_function, division
import random

__author__ = 'Ben Lai'
__email__ = "laichunpongben@gmail.com"


class ColorMap(object):
    '''
    Apply genetic algorithm to find to four-color the map.
    Fitness is defined by the ratio of different color between adjacent blocks.
    By the four color theorem, there exists at least one solution.
    If the coloring is not found in a run,
    try re-run with different parameters
    such as chromosome_size and max_no_update_generation.
    '''

    COLORS = ['+', '-', '*', '/']

    def __init__(self, map_path, **kwargs):
        self.chromosome_size = kwargs.get('chromosome_size', 100)
        self.max_generation = kwargs.get('max_generation', 2000)
        self.max_no_update_generation = kwargs.get('max_no_update_generation', 500)
        self.success_threshold = kwargs.get('success_threshold', 1.0)
        self.mutation_ratio = kwargs.get('mutation_ratio', 0.1)
        self.map = self.load_map(map_path)
        self.height = len(self.map)
        self.width = len(self.map[0])
        self.blocks = self.get_blocks()
        self.adjacency = self.get_adjacency()
        self.chromosomes = self.init_chromosomes()
        self.last_updated_generation = 0

    @staticmethod
    def load_map(map_path):
        with open(map_path, 'r') as f:
            map_ = f.read()
        map_ = [line for line in map_.split('\n') if line]
        return map_

    def get_blocks(self):
        return ''.join(sorted(list(set(''.join(self.map)))))

    def get_adjacency(self):
        adjacency = []
        for y in range(self.height):
            for x in range(self.width):
                if x < self.width - 1 and self.map[y][x] != self.map[y][x+1]:
                    adjacency.append(tuple(sorted([self.map[y][x], self.map[y][x+1]])))
                if y < self.height - 1 and self.map[y][x] != self.map[y+1][x]:
                    adjacency.append(tuple(sorted([self.map[y][x], self.map[y+1][x]])))
        return sorted(list(set(adjacency)))

    def random_chromosome(self):
        return ''.join([random.choice(self.COLORS) for _ in range(len(self.blocks))])

    def init_chromosomes(self):
        return [self.random_chromosome() for _ in range(self.chromosome_size)]

    def get_block_color_dict(self, chromosome):
        return dict(zip(self.blocks, chromosome))

    def fitness(self, chromosome):
        d = self.get_block_color_dict(chromosome)
        count = 0
        for block0, block1 in self.adjacency:
            if d[block0] != d[block1]:
                count += 1
        return count / len(self.adjacency)

    def crossover(self, chromosome0, chromosome1):
        index = int(random.uniform(0, 1) * len(self.blocks))
        child_chromosome0 = chromosome0[:index] + chromosome1[index:]
        child_chromosome1 = chromosome1[:index] + chromosome0[index:]
        return child_chromosome0, child_chromosome1

    def mutate(self, chromosome):
        mutation = int(round(self.mutation_ratio * len(self.blocks)))
        chromosome_ = chromosome
        for _ in range(mutation):
            index = int(random.uniform(0, 1) * len(self.blocks))
            old_color = chromosome_[index]
            colors = self.COLORS[:]
            colors.remove(old_color)
            new_color = random.choice(colors)
            chromosome_ = chromosome_[:index] + new_color + chromosome_[index+1:]
        return chromosome_

    @staticmethod
    def chunker(str, size):
        return (str[index:index + size] for index in range(0, len(str), size))

    def make_map(self, chromosome):
        map_string = ''.join(self.map)
        d = self.get_block_color_dict(chromosome)
        for k, v in d.items():
            map_string = map_string.replace(k, v)
        return list(self.chunker(map_string, self.width))

    @staticmethod
    def normalize_map(map):
        return '\n'.join(map)

    def solve(self):
        best_chromosome = self.COLORS[0] * len(self.blocks)
        best_fitness = 0.0
        for i in range(self.max_generation):
            chromosome_fitnesses = []
            for chromosome in self.chromosomes:
                fitness = self.fitness(chromosome)
                chromosome_fitnesses.append((chromosome, fitness))
            random.shuffle(chromosome_fitnesses)

            for j in range(int(self.chromosome_size / 2)):
                children_chromosomes = self.crossover(chromosome_fitnesses[j*2][0], chromosome_fitnesses[j*2+1][0])
                for chromosome in children_chromosomes:
                    chromosome = self.mutate(chromosome)
                    fitness = self.fitness(chromosome)
                    chromosome_fitnesses.append((chromosome, fitness))
            chromosome_fitnesses.sort(key=lambda x: -x[1])
            self.chromosomes = list(list(zip(*chromosome_fitnesses))[0])[:self.chromosome_size]
            best_trial_fitness = chromosome_fitnesses[0][1]

            print('Generation {0}: {1} {2}'.format(i, chromosome_fitnesses[0][0], chromosome_fitnesses[0][1]))
            if best_trial_fitness > best_fitness:
                best_chromosome, best_fitness = chromosome_fitnesses[0][0], chromosome_fitnesses[0][1]
                self.last_updated_generation = i

            if best_fitness >= 1.0:
                break

            if i - self.last_updated_generation > self.max_no_update_generation:
                break

        best_color_map = self.normalize_map(self.make_map(best_chromosome))

        return best_chromosome, best_fitness, best_color_map

    @staticmethod
    def save(normalized_map, path):
        with open(path, 'w') as f:
            f.write(normalized_map)

    def extend_map(self, multiplier):
        extended_map = []
        for y in range(self.height):
            line = ''
            for x in range(self.width):
                line += self.map[y][x] * multiplier
            extended_map.extend([line] * multiplier)
        return extended_map

if __name__ == '__main__':
    import time

    start = time.time()

    map_path = 'q1/map.txt'
    color_map = ColorMap(map_path)
    # print('Testing functions...')
    # print(color_map.height)
    # print(color_map.width)
    # print(color_map.blocks)
    # print(color_map.adjacency)
    # print(color_map.chromosomes)
    # print(color_map.fitness(color_map.chromosomes[0]))
    # extended_map = color_map.normalize_map(color_map.extend_map(10))
    # color_map.save(extended_map, 'q1/extended_map.txt')

    print('Start coloring...')
    chromosome, fitness, map_ = color_map.solve()

    if fitness >= color_map.success_threshold:
        print('Coloring done!')
    else:
        print('Coloring is unsuccessful!')

    print(map_)
    output_path = 'q1/color_map.txt'
    color_map.save(map_, output_path)

    end = time.time()
    lapsed_sec = end - start
    print('Lapsed sec: {0}'.format(lapsed_sec))
