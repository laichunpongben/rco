#!/usr/bin/python3

from __future__ import print_function, division
import re
import math
import operator


class AlgebraCalculator(object):
    def __init__(self):
        self.expression = None
        self.status = None
        # self.paren = self.paren_matcher(25)
        self.op = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul
        }

    def parse_parenthesis(self, expression, level=0, index=0):
        print(level, index, expression)
        stack = dict()

        if not '(' in expression or not ')' in expression:
            return

        counter = 0
        index_start, index_end = 0, 0
        for index, c in enumerate(expression):
            if c == '(':
                counter += 1
                if counter == 1:
                    index_start = index+1
            elif c == ')':
                counter += -1
                if counter == 0:
                    index_end = index
                    sub_expression = expression[index_start:index_end]
                    self.parse_parenthesis(sub_expression, level+1, index_start)
            if counter < 0:
                print()
                return

            # print(index, c, counter)

        return stack

    # @staticmethod
    # def paren_matcher(n):
    #     return re.compile(r"[^()]*?(?:\("*n+r"[^()]*?"+r"\)[^()]*?)*?"*n)



    def add(self, x, y):
        pass

    def subtract(self, x, y):
        pass

    @staticmethod
    def multiply(expression0, expression1):
        x = Polynomial(expression0)
        y = Polynomial(expression1)
        coefficient = x.coefficient * y.coefficient
        variables = {k: x.variables.get(k, 0) + y.variables.get(k, 0)
                     for k in set(x.variables) | set(y.variables)}
        constant = x.constant + y.constant
        print('con', type(x.constant), type(y.constant))
        expression = Polynomial(None, coefficient=coefficient, variables=variables, constant=constant)
        return expression.expression

    def calc(self, expression):
        self.expression = expression
        # print(self.paren.match(expression))

    @staticmethod
    def string_to_dict(param_str):
        d = dict()
        param_strs = param_str.split(',')
        for s in param_strs:
            k, v = s.split('=')
            d[k] = v
        return d

    def eval_stack(self, stack):
        pass

    def eval(self, status):
        # self.status = status
        params = self.string_to_dict(status)


class Polynomial(object):
    def __init__(self, expression=None, **kwargs):
        self.terms = []
        if expression:
            self.terms = self.parse(expression)
        else:
            self.terms = kwargs.get('terms', [])
        self.expression = self.__str__()

    def __str__(self):
        expression = ''
        for index, term in enumerate(self.terms):
            if index > 0:
                if term.coefficient > 0:
                    expression += '+'
                    expression += term.expression
                elif term.coefficient < 0:
                    expression += term.expression
                else:
                    if term.constant >= 0:
                        expression += '+'
                        expression += term.expression
                    else:
                        expression += term.expression
            else:
                expression += term.expression
        return expression

    @staticmethod
    def parse(expression):
        term_expressions = []
        elements = re.split(r"(\+[^\+\-\*]+|\-[^\+\-\*]+|\*)", expression)
        for x in elements:
            if x:
                if x.startswith('+'):
                    term_expressions.append(x[1:])
                else:
                    term_expressions.append(x)
        print(term_expressions)

        terms = [Term(expression) for expression in term_expressions]
        return terms

    def add(self, polynomial):
        terms = sorted(self.terms[:] + polynomial.terms[:], key=lambda x: x.variables)
        return Polynomial(None, terms=terms)

    def subtract(self, polynomial):
        new_terms = []
        for term in polynomial.terms:
            if term.coefficient == 0:
                term_ = Term(None, coefficient=0, variables={}, constant=-term.constant)
            else:
                term_ = Term(None, coefficient=-term.coefficient, variables=term.variables, constant=term.constant)
            new_terms.append(term_)

        terms = sorted(self.terms + new_terms, key=lambda x: x.variables)
        return Polynomial(None, terms=terms)

    def multiply(self, polynomial):
        terms = []
        return Polynomial(None, terms=terms)

class Term(object):
    def __init__(self, expression=None, **kwargs):
        self.coefficient = 0
        self.variables = {}
        self.constant = 0
        if expression:
            self.coefficient, self.variables, self.constant = self.parse(expression)
        else:
            self.coefficient = kwargs.get('coefficient', 0)
            self.variables = kwargs.get('variables', {})
            self.constant = kwargs.get('constant', 0)
        self.expression = self.__str__()

    def __str__(self):
        expression = ''
        if not -1 <= self.coefficient <= 1:
            expression += str(self.coefficient)
        if self.coefficient == -1:
            expression += '-'
        for k, v in sorted(self.variables.items()):
            if v != 0:
                expression += k
                if v != 1:
                    expression += str(v)
        if self.constant != 0 or not expression:
            expression += str(self.constant)
        return expression

    def __eq__(self, term):
        if self is term:
            return True
        elif not isinstance(term, self.__class__):
            return False
        elif self.coefficient == term.coefficient and \
             self.variables == term.variables and \
             self.constant == term.constant:
            return True
        else:
            return False

    def __hash__(self):
        result = 17
        result = result * 31 + self.coefficient
        for k, v in sorted(self.variables.items()):
            result = result * 31 +  ord(k) * v
        result = result * 31 + self.constant
        return result

    @staticmethod
    def parse(expression):
        elements = re.split(r"([a-z])", expression)
        normalized_elements = []
        for x in elements:
            if x == '':
                normalized_elements.append('1')
            elif x == '-':
                normalized_elements.append('-1')
            else:
                normalized_elements.append(x)

        if any(x.isalpha() for x in normalized_elements):
            variables = {}
            for i in range(int(len(normalized_elements)/2)):
                variables[normalized_elements[i*2+1]] = int(normalized_elements[i*2+2])
            return int(normalized_elements[0]), variables, 0
        else:
            return 0, {}, int(normalized_elements[0])

    def add(self, term):
        if self.variables == term.variables:
            if self.variables:
                coefficient = self.coefficient + term.coefficient
                if coefficient == 0:
                    return Term(None, coefficient=0, variables={}, constant=0)
                else:
                    return Term(None, coefficient=coefficient, variables=self.variables, constant=0)
            else:
                return Term(None, coefficient=0, variables={}, constant=self.constant + term.constant)
        else:
            return Polynomial(None, terms=[self, term])

    def subtract(self, term):
        if self.variables == term.variables:
            if self.variables:
                coefficient = self.coefficient - term.coefficient
                if coefficient == 0:
                    return Term(None, coefficient=0, variables={}, constant=0)
                else:
                    return Term(None, coefficient=coefficient, variables=self.variables, constant=0)
            else:
                return Term(None, coefficient=0, variables={}, constant=self.constant - term.constant)
        else:
            term_ = Term(None, coefficient=-term.coefficient, variables=term.variables, constant=term.constant)
            return Polynomial(None, terms=[self, term_])

    def multiply(self, term):
        coefficient = self.coefficient * term.coefficient
        variables = {k: self.variables.get(k, 0) + term.variables.get(k, 0)
                     for k in set(self.variables) | set(term.variables)}
        return Term(None, coefficient=coefficient, variables=variables, constant=0)

if __name__ == '__main__':
    expression = 'a+4-b+(12+(10+c)+d)+((2*e)+3*f)'
    statuses = [
        'a=5,b=3,c=2',
        'a=2,b=9,c=-7',
        'a=-5,c=-9',
        'a=-3,c=-10',
        'a=-5,c=-10',
    ]

    calculator = AlgebraCalculator()
    calculator.parse_parenthesis(expression)

    print(Term('4a'))
    print(Term('2ab'))
    print(Term('a2b2'))
    print(Term('-a'))

    print(Polynomial('4a'))
    print(Polynomial('2ab'))
    print(Polynomial('a2b2'))
    print(Polynomial('0'))
    print(Polynomial('10'))
    print(Polynomial('101a3'))
    print(Polynomial('-99b3'))
    print(Polynomial('-99b3+2'))
    print(Polynomial('-99b3-2'))
    print(Polynomial('a+b-c+1'))
    print(Polynomial('-1'))

    print(Term('4a').add(Term('a')))
    print(Term('4a').add(Term('b')))
    print(Term('-a').add(Term('b')))
    print(Term('b').add(Term('-a')))
    print(Term('a').add(Term('-b')))
    print(Term('a').add(Term('-a')))
    print(Term('a').multiply(Term('-b')))
    print(Term('-a').multiply(Term('-b')))
    print(Term('2a').subtract(Term('a')))
    print(Term('a').subtract(Term('a')))
    print(Term('a').subtract(Term('b')))
    print(Term('5').subtract(Term('1')))
    print(Term('3').subtract(Term('6')))
    print(Term('4a').add(Term('a')).subtract(Term('6a')))
    print(Term('a') == Term('a'))
    print(Term('a') == Term('b'))
    print(Term('0') == Term('0'))
    print(Term('4ab2') == Term('4b2a'))
    print(Term('4ab2').__hash__())
    print(Term('4b2a').__hash__())

    # print(Polynomial('a').add(Polynomial('b')))
    # print(Polynomial('a').add(Polynomial('2a')))

    # print(AlgebraCalculator.multiply('1', '2'))
    # print(AlgebraCalculator.multiply('1', '0'))


    # calculator.calc(expression)

    # for status in statuses:
    #     print(calculator.eval(status))
