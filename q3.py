#!/usr/bin/python3

from __future__ import print_function, division
import string
import random
from collections import Counter


class SubstitutionCipherSolver(object):
    def __init__(self, cipher_text, words, **kwargs):
        self.cipher_text = cipher_text
        self.words = words
        self.plain_text = ''
        self.max_generation = kwargs.get('max_generation', 1000)
        self.key_population_size = kwargs.get('key_population_size', 50)
        self.min_decrpytion_ratio = kwargs.get('min_decrpytion_ratio', 0.1)
        self.max_no_update_generation = kwargs.get('max_no_update_generation', 100)
        self.key_population = [self.shuffle(string.ascii_lowercase) for _ in range(self.key_population_size)]
        self.non_ascii_letter_key = self.get_non_ascii_letter_key(self.cipher_text)
        self.last_updated_generation = 0

    @staticmethod
    def get_non_ascii_letter_key(text):
        chars = sorted(list(set(text.lower())))
        non_ascii_letters = [c for c in chars if c not in string.ascii_lowercase]
        return ''.join(non_ascii_letters)

    @staticmethod
    def shuffle(key):
        return ''.join(random.sample(key, len(key)))

    @staticmethod
    def swap(key):
        c0, c1 = random.sample(key, 2)
        index_c0 = key.index(c0)
        index_c1 = key.index(c1)
        chars = list(key)
        chars[index_c0], chars[index_c1] = chars[index_c1], chars[index_c0]
        return ''.join(chars)

    def extend(self, key):
        return key + key.upper() + self.non_ascii_letter_key

    def encrypt(self, key):
        alphabet = self.extend(string.ascii_lowercase)
        key_ = self.extend(key)
        key_indices = [alphabet.index(c) for c in self.plain_text]
        return ''.join(key_[index] for index in key_indices)

    def decrypt(self, key):
        alphabet = self.extend(string.ascii_lowercase)
        key_ = self.extend(key)
        key_indices = [key_.index(c) for c in self.cipher_text]
        return ''.join(alphabet[index] for index in key_indices)

    @staticmethod
    def remove_non_ascii(text):
        return ''.join([c if ord(c) < 128 else ' ' for c in text])

    def calc_fitness(self, decrypted_text):
        count = 0
        normalized_decrpyted_text = self.remove_non_ascii(decrypted_text.lower())
        decrypted_words = list(set(normalized_decrpyted_text.split(' ')))
        for word in decrypted_words:
            if word in self.words:
                count += 1
        return count / len(self.words)

    def crossover(self, key0, key1):
        len_key = len(string.ascii_lowercase)
        index = int(random.uniform(0, 1) * len_key)
        child_key0 = key0[:index] + key1[index:]
        child_key1 = key1[:index] + key0[index:]
        child_key0 = self.normalize(child_key0)
        child_key1 = self.normalize(child_key1)
        return child_key0, child_key1

    def mutate(self, key):
        return self.swap(key)

    @staticmethod
    def normalize(key):
        d = Counter(key)
        duplicate_chars = [k for k, v in d.items() if v >= 2]
        missing_chars = list(set(string.ascii_lowercase).difference(set(d.keys())))
        random.shuffle(missing_chars)
        for i in range(len(duplicate_chars)):
            index0 = key.index(duplicate_chars[i])
            index1 = key.index(duplicate_chars[i], index0 + 1)
            index = random.choice((index0, index1))
            key = key[:index] + missing_chars[i] + key[index+1:]
        return key

    def solve(self):
        best_key = string.ascii_lowercase
        best_fitness = 0.0
        for i in range(self.max_generation):
            key_fitnesses = []
            for key in self.key_population:
                decrypted_text = self.decrypt(key)
                fitness = self.calc_fitness(decrypted_text)
                key_fitnesses.append((key, fitness))
            key_fitnesses.sort(key=lambda x: -x[1])

            for j in range(int(self.key_population_size / 2)):
                children_keys = self.crossover(key_fitnesses[j*2][0], key_fitnesses[j*2+1][0])
                for key in children_keys:
                    key = self.mutate(key)
                    decrypted_text = self.decrypt(key)
                    fitness = self.calc_fitness(decrypted_text)
                    key_fitnesses.append((key, fitness))
            key_fitnesses.sort(key=lambda x: -x[1])
            self.key_population = list(list(zip(*key_fitnesses))[0])[:self.key_population_size]
            best_trial_fitness = key_fitnesses[0][1]

            print('Generation {0}: {1} {2}'.format(i, key_fitnesses[0][0], key_fitnesses[0][1]))
            if best_trial_fitness > best_fitness:
                best_key, best_fitness = key_fitnesses[0][0], key_fitnesses[0][1]
                self.last_updated_generation = i

            if best_fitness >= 1.0:
                break

            if i - self.last_updated_generation > self.max_no_update_generation:
                break

        return best_key, best_fitness

if __name__ == '__main__':
    import time

    start = time.time()

    cipher_path = 'q3/question.txt'
    with open(cipher_path, 'r') as f1:
        cipher_text = f1.read()
    print(cipher_text)

    dict_path = 'q3/dict.txt'
    with open(dict_path, 'r') as f2:
        word_text = f2.read()
        words = sorted(list(set(word_text.strip().split(' '))))
    print(words)

    solver = SubstitutionCipherSolver(cipher_text, words)
    # print('Testing functions...')
    # print(solver.swap('abcdef'))
    # print(solver.shuffle('1234567890'))
    # print(solver.decrypt('fbavxposmyzkdjcnrquhtgweil'))
    # print(solver.crossover(string.ascii_lowercase, 'fbavxposmyzkdjcnrquhtgweil'))
    # print(solver.normalize('fbavxposmyzkdjcnrquhtgweix'))
    # print()

    print('Start solving...')
    key, fitness = solver.solve()

    if fitness >= solver.min_decrpytion_ratio:
        print('Decryption successful! Key found!')
    else:
        print('Decryption unsuccessful! Key not found!')

    print('Result key: {0}'.format(key))
    print('Best fitness: {0}'.format(fitness))
    print()

    plain_text = solver.decrypt(key)
    print(plain_text)

    end = time.time()
    lapsed_sec = end - start
    print('Lapsed sec: {0}'.format(lapsed_sec))
