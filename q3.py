#!/usr/bin/python3

from __future__ import print_function, division
import string
import random
from collections import Counter

__author__ = 'Ben Lai'
__email__ = "laichunpongben@gmail.com"


class SubstitutionCipherSolver(object):
    '''
    Apply genetic algorithm to find the key of the substitution cipher.
    Fitness is defined by the ratio of decrypted words found in the dictionary.
    Alternatively, if a dictionary is not available,
    fitness can be defined by 1 - cross-entropy
    of letters against a common distribution. (NotImplemented)
    If the key is not found in a run,
    try re-run with different parameters
    such as chromosome_size and max_no_update_generation.
    '''

    def __init__(self, cipher_text, words, **kwargs):
        self.cipher_text = cipher_text
        self.words = words
        self.plain_text = ''
        self.max_generation = kwargs.get('max_generation', 1000)
        self.chromosome_size = kwargs.get('chromosome_size', 40)  # must be even int
        self.success_threshold = kwargs.get('success_threshold', 0.1)
        self.max_no_update_generation = kwargs.get('max_no_update_generation', 100)
        self.mutate_swap = kwargs.get('mutate_swap', 1)
        self.chromosomes = [self.shuffle(string.ascii_lowercase) for _ in range(self.chromosome_size)]
        self.non_ascii_letter_key = self.get_non_ascii_letter_key(self.cipher_text)
        self.normalized_cipher_text = self.normalize_text(self.cipher_text)
        self.alphabet = self.extend(string.ascii_lowercase)
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

    def encrypt(self, key, text):
        key_ = self.extend(key)
        return text.translate(str.maketrans(self.alphabet, key_))

    def decrypt(self, key, text):
        key_ = self.extend(key)
        return text.translate(str.maketrans(key_, self.alphabet))

    @staticmethod
    def remove_non_ascii(text):
        return ''.join([c if ord(c) < 128 else ' ' for c in text])

    @staticmethod
    def remove_punctuation(text):
        text_ = text.translate(str.maketrans('', '', string.punctuation))
        text_ = text_.replace('\n', ' ')
        return text_

    @staticmethod
    def remove_digits(text):
        return text.translate(str.maketrans('', '', string.digits))

    def normalize_text(self, text):
        text_ = self.remove_non_ascii(text.lower())
        text_ = self.remove_punctuation(text_)
        text_ = self.remove_digits(text_)
        return text_

    def fitness(self, normalized_decrypted_text):
        count = 0
        decrypted_words = [word for word in list(set(normalized_decrypted_text.split(' '))) if word]
        for word in decrypted_words:
            if word in self.words:
                count += 1
        return count / len(self.words)

    def crossover(self, key0, key1):
        len_key = len(string.ascii_lowercase)
        index = int(random.uniform(0, 1) * len_key)
        child_key0 = key0[:index] + key1[index:]
        child_key1 = key1[:index] + key0[index:]
        child_key0 = self.normalize_key(child_key0)
        child_key1 = self.normalize_key(child_key1)
        return child_key0, child_key1

    def mutate(self, key):
        key_ = key
        for _ in range(self.mutate_swap):
            key_ = self.swap(key_)
        return key_

    @staticmethod
    def normalize_key(key):
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
            for key in self.chromosomes:
                normalized_decrypted_text = self.decrypt(key, self.normalized_cipher_text)
                fitness = self.fitness(normalized_decrypted_text)
                key_fitnesses.append((key, fitness))
            random.shuffle(key_fitnesses)

            for j in range(int(self.chromosome_size / 2)):
                children_keys = self.crossover(key_fitnesses[j*2][0], key_fitnesses[j*2+1][0])
                for key in children_keys:
                    key = self.mutate(key)
                    normalized_decrypted_text = self.decrypt(key, self.normalized_cipher_text)
                    fitness = self.fitness(normalized_decrypted_text)
                    key_fitnesses.append((key, fitness))
            key_fitnesses.sort(key=lambda x: -x[1])
            self.chromosomes = list(list(zip(*key_fitnesses))[0])[:self.chromosome_size]
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
    # print(solver.decrypt('fbavxposmyzkdjcnrquhtgweil', solver.cipher_text))
    # print(solver.crossover(string.ascii_lowercase, 'fbavxposmyzkdjcnrquhtgweil'))
    # print(solver.normalize_key('fbavxposmyzkdjcnrquhtgweix'))
    # print()

    print('Start solving...')
    key, fitness = solver.solve()

    if fitness >= solver.success_threshold:
        print('Decryption successful! Key found!')
    else:
        print('Decryption unsuccessful! Key not found!')

    print('Result key: {0}'.format(key))
    print('Best fitness: {0}'.format(fitness))
    print()

    plain_text = solver.decrypt(key, solver.cipher_text)
    print(plain_text)

    end = time.time()
    lapsed_sec = end - start
    print('Lapsed sec: {0}'.format(lapsed_sec))
