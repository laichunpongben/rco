#!/usr/bin/python3

from __future__ import print_function, division
import re
import math
import operator
from copy import deepcopy

__author__ = 'Ben Lai'
__email__ = "laichunpongben@gmail.com"


class Algebra(object):
    def __init__(self, expression):
        self.expression = expression
        self.children = []
        self.polynomial = None
        self.parse(self.expression)
        self.regex_children = self.get_regex_children()
        self.calc()

    def __str__(self):
        return self.expression

    def parse(self, expression):
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
                    algebra = Algebra(expression[index_start:index_end])
                    self.children.append(algebra)
            if counter < 0:
                return
        return

    def get_regex_children(self):
        regex = r"("
        for index, child in enumerate(self.children):
            if index > 0:
                regex += r"|"
            regex += r"\(" + re.escape(child.expression) + r"\)"
        regex += r")"
        return re.compile(regex)

    def calc(self):
        while not self.polynomial:
            if self.children:
                if all(child.polynomial for child in self.children):
                    expressions = re.split(self.regex_children, self.expression)
                    for child in self.children:
                        for index, expression in enumerate(expressions):
                            if expression == '(' + child.expression + ')':
                                expressions = expressions[:index] + [child.polynomial] + expressions[index+1:]

                    polynomials = []
                    for expression in expressions:
                        if not isinstance(expression, Polynomial):
                            elements = re.split(r"([\+\-\*])", expression)
                            polynomials.extend(elements)
                        else:
                            polynomials.append(expression)
                    polynomials = [p for p in polynomials if p or p == '0']
                    polynomials = [Polynomial(p) if not isinstance(p, Polynomial) and
                                   p not in ['+', '-', '*'] else p for p in polynomials]

                    index = 0
                    while '*' in polynomials:
                        if index == len(polynomials) - 1:
                            break

                        if polynomials[index] == '*':
                            polynomial = polynomials[index-1].multiply(polynomials[index+1])
                            polynomials = polynomials[:index-1] + [polynomial] + polynomials[index+2:]
                            index += -1
                        index += 1

                    index = 0
                    while len(polynomials) > 1:
                        if index == len(polynomials) - 1:
                            break

                        if polynomials[index] == '+':
                            if index == 0:
                                polynomials = polynomials[index+1:]
                            else:
                                polynomial = polynomials[index-1].add(polynomials[index+1])
                                polynomials = polynomials[:index-1] + [polynomial] + polynomials[index+2:]
                            index += -1
                        elif polynomials[index] == '-':
                            if index == 0:
                                polynomial = polynomials[index+1].multiply(Polynomial('-1'))
                                polynomials = [polynomial] + polynomials[index+2:]
                            else:
                                polynomial = polynomials[index-1].subtract(polynomials[index+1])
                                polynomials = polynomials[:index-1] + [polynomial] + polynomials[index+2:]
                            index += -1
                        index += 1

                    self.polynomial = polynomials[0]
                else:
                    for child in self.children:
                        if not child.polynomial:
                            child.calc()
            else:
                self.polynomial = Polynomial(self.expression)

    @staticmethod
    def string_to_dict(param_str):
        return dict((k, int(v)) for k, v in (item.split('=') for item in param_str.split(',')))

    def eval(self, params):
        return self.polynomial.eval(params)

    def eval_str(self, param_str):
        params = self.string_to_dict(param_str)
        return self.eval(params)

class Polynomial(object):
    OPERATORS = re.compile(r"(\+|\-|\*)")

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
                    if term.constant > 0:
                        expression += '+'
                        expression += term.expression
                    elif term.constant < 0:
                        expression += term.expression
                    else:
                        pass
            else:
                expression += term.expression
        return expression

    def __eq__(self, polynomial):
        if self is polynomial:
            return True
        elif not isinstance(polynomial, self.__class__):
            return False
        elif self.terms == polynomial.terms:
            return True
        else:
            return False

    def __hash__(self):
        result = 17
        for term in sorted(self.terms):
            result = result * 31 + term.__hash__()
        return result

    @staticmethod
    def parse(expression):
        term_expressions = []
        elements = re.split(Polynomial.OPERATORS, expression)
        elements_ = [x for x in elements if x]

        index = 0
        while True:
            if index == len(elements_) - 1:
                break
            if not any(x in elements_ for x in ['*', '+', '-']):
                break

            if elements_[index] == '*':
                term = Term(elements_[index-1]).multiply(Term(elements_[index+1]))
                elements_ = elements_[:index-1] + [term.expression] + elements_[index+2:]
                index = 0
            elif elements_[index] == '-':
                term = Term(elements_[index+1]).multiply(Term('-1'))
                elements_ = elements_[:index] + [term.expression] + elements_[index+2:]
                index = 0
            elif elements_[index] == '+':
                elements_ = elements_[:index] + elements_[index+1:]
                index = 0
            else:
                index += 1

        for x in elements_:
            if x:
                if x.startswith('+'):
                    term_expressions.append(x[1:])
                else:
                    term_expressions.append(x)

        terms = [Term(expression) for expression in term_expressions]
        return terms

    def add(self, polynomial):
        terms = sorted(self.terms[:] + polynomial.terms[:], reverse=True)
        terms = self.reduce(terms)
        return Polynomial(None, terms=terms)

    def subtract(self, polynomial):
        new_terms = []
        for term in polynomial.terms:
            if term.coefficient == 0:
                term_ = Term(None, coefficient=0, variables={}, constant=-term.constant)
            else:
                term_ = Term(None, coefficient=-term.coefficient, variables=term.variables, constant=term.constant)
            new_terms.append(term_)

        terms = sorted(self.terms + new_terms, reverse=True)
        terms = self.reduce(terms)
        return Polynomial(None, terms=terms)

    def multiply(self, polynomial):
        terms = []
        for term0 in self.terms:
            for term1 in polynomial.terms:
                term = term0.multiply(term1)
                terms.append(term)
        terms = self.reduce(terms)
        return Polynomial(None, terms=terms)

    @staticmethod
    def reduce(terms):
        terms_ = terms[:]
        index = 0
        while True:
            if index == len(terms_) - 1:
                break
            if terms_[index].variables == terms_[index+1].variables:
                term = terms_[index].add(terms_[index+1])
                terms_ = terms_[:index] + [term] + terms_[index+2:]
                index += -1
            index += 1

        terms_ = [term for term in terms_ if term.coefficient != 0 or term.constant != 0]
        if not terms_:
            terms_ = [Term(None, coefficient=0, variables={}, constant=0)]

        return terms_

    def eval(self, params):
        terms = sorted([term.eval(params) for term in self.terms], reverse=True)
        terms = self.reduce(terms)
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
        if self.coefficient != 0:
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

    def __lt__(self, term):
        if self.variables and term.variables:
            count0 = 17
            for k, v in sorted(self.variables.items()):
                for _ in range(v):
                    count0 = count0 * 31 + (128 - ord(k))

            count1 = 17
            for k, v in sorted(term.variables.items()):
                for _ in range(v):
                    count1 = count1 * 31 + (128 - ord(k))

            if count0 < count1:
                return True
            elif count0 > count1:
                return False
            else:
                if self.coefficient < term.coefficient:
                    return True
                else:
                    return False
        elif self.variables and not term.variables:
            return False
        elif not self.variables and term.variables:
            return True
        else:
            if self.constant < term.constant:
                return True
            else:
                return False

    def __le__(self, term):
        if self.variables and term.variables:
            count0 = 17
            for k, v in sorted(self.variables.items()):
                for _ in range(v):
                    count0 = count0 * 31 + (128 - ord(k))

            count1 = 17
            for k, v in sorted(term.variables.items()):
                for _ in range(v):
                    count1 = count1 * 31 + (128 - ord(k))

            if count0 < count1:
                return True
            elif count0 > count1:
                return False
            else:
                if self.coefficient <= term.coefficient:
                    return True
                else:
                    return False
        elif self.variables and not term.variables:
            return False
        elif not self.variables and term.variables:
            return True
        else:
            if self.constant <= term.constant:
                return True
            else:
                return False

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
        if self.variables and term.variables:
            coefficient = self.coefficient * term.coefficient
            variables = {k: self.variables.get(k, 0) + term.variables.get(k, 0)
                         for k in set(self.variables) | set(term.variables)}
            return Term(None, coefficient=coefficient, variables=variables, constant=0)
        elif self.variables and not term.variables:
            coefficient = self.coefficient * term.constant
            return Term(None, coefficient=coefficient, variables=self.variables, constant=0)
        elif not self.variables and term.variables:
            coefficient = self.constant * term.coefficient
            return Term(None, coefficient=coefficient, variables=term.variables, constant=0)
        else:
            constant = self.constant * term.constant
            return Term(None, coefficient=0, variables={}, constant=constant)

    def eval(self, params):
        if self.variables:
            coefficient = self.coefficient
            variables = deepcopy(self.variables)
            for k, v in sorted(variables.items()):
                if k in params.keys():
                    coefficient *= params[k] ** v
                    variables.pop(k)
            if variables:
                return Term(None, coefficient=coefficient, variables=variables, constant=0)
            else:
                return Term(None, coefficient=0, variables={}, constant=coefficient)
        else:
            return deepcopy(self)

if __name__ == '__main__':
    expression = 'a+4-b+(12+(10+c)+d)+((2*e)+3*f)'
    statuses = [
        'a=5,b=3,c=2',
        'a=2,b=9,c=-7',
        'a=-5,c=-9',
        'a=-3,c=-10',
        'a=-5,c=-10',
    ]

    algebra = Algebra(expression)
    print(algebra.polynomial.expression)

    print(algebra.string_to_dict('a=1,b=2'))
    print(algebra.eval_str('a=1,b=2'))

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
    print(Term('a').add(Term('1')))
    print(Term('8').add(Term('1')))
    print(Term('a').multiply(Term('-b')))
    print(Term('-a').multiply(Term('-b')))
    print(Term('a').multiply(Term('2')))
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
    print(Term('1') < Term('2'))
    print(Term('a') < Term('b'))
    print(Term('a2') < Term('4b'))

    print(Polynomial('a').add(Polynomial('b')))
    print(Polynomial('a').add(Polynomial('b+1')))
    print(Polynomial('a').add(Polynomial('2a+1')))
    print(Polynomial('a').subtract(Polynomial('b')))
    print(Polynomial('1').subtract(Polynomial('2b')))
    print(Polynomial('a').subtract(Polynomial('2a')))
    print(Polynomial('a').subtract(Polynomial('2a+1')).add(Polynomial('b')))
    print(Polynomial('a').multiply(Polynomial('a')))
    print(Polynomial('a').multiply(Polynomial('b')))
    print(Polynomial('a2').multiply(Polynomial('b3')))
    print(Polynomial('a+1').multiply(Polynomial('b+1')))
    print(Polynomial('a+2').multiply(Polynomial('b+1')))
    print(Polynomial('a+2').multiply(Polynomial('a+1')))
    print(Polynomial('a+2').multiply(Polynomial('a-1')))
    print(Polynomial('a2+a+2').multiply(Polynomial('a-1')))

    print(Term('4ab').eval(dict(a=2, b=3)))
    print(Term('4ab').eval(dict(a=2)))
    print(Term('4ab').eval(dict(a=0)))

    print(Term('2cf') < Term('2de'))
    print(Term('2cf') <= Term('2de'))
    print(Term('2de') < Term('cf'))
    print(Term('2de') <= Term('cf'))

    print(Polynomial('4ab').eval(dict(a=1,b=2)))
    print(Polynomial('4ab+1').eval(dict(a=1,b=2)))
    print(Polynomial('-3ab+b+1').eval(dict(a=1,b=2)))
    print(Polynomial('-3ab+b+1').eval(dict(a=1)))

    print(Polynomial('2a') == Polynomial('2a'))
    print(Polynomial('ab') == Polynomial('ba'))
    print(Polynomial('0') == Polynomial('1'))

    print(Polynomial('4x*5y'))
    print(Polynomial('4x*5y+1'))
    print(Polynomial('z+4x*5y+1'))
    print(Polynomial('z+4x*5y+2a*3b+1'))

    p0 = Polynomial('a+4-b+10+c')
    print(p0.eval(dict(a=5,b=3,c=2)))
    print(p0.eval(dict(a=2,b=9,c=-7)))
    print(p0.eval(dict(a=-5,c=-9)))
    print(p0.eval(dict(a=-3,c=-10)))
    print(p0.eval(dict(a=-5,c=-10)))

    p3 = Polynomial('z+x-x+y+y')
    print(p3.eval(dict(x=-11,z=0)))
    print(p3.eval(dict(x=11,z=4)))
    print(p3.eval(dict(y=-9,z=0)))
    print(p3.eval(dict(y=9,z=13)))

    p7 = Polynomial('a*b*x+a*b*y')
    print(p7.eval(dict(a=1,b=2,x=5,y=10)))
    print(p7.eval(dict(x=5,y=10)))
    print(p7.eval(dict(x=5,y=-10)))
    print(p7.eval(dict(a=10,b=-5)))
    print(p7.eval(dict(b=-20)))

    print()

    a0 = Algebra('a+4-b+10+c')
    print('Case 0:', a0)
    print(a0.eval_str('a=5,b=3,c=2'))
    print(a0.eval_str('a=2,b=9,c=-7'))
    print(a0.eval_str('a=-5,c=-9'))
    print(a0.eval_str('a=-3,c=-10'))
    print(a0.eval_str('a=-5,c=-10'))
    print()

    a1 = Algebra('x+4-(y-30)')
    print('Case 1:', a1)
    print(a1.eval_str('x=1,y=0'))
    print(a1.eval_str('x=5'))
    print(a1.eval_str('y=-2'))
    print(a1.eval_str('z=10'))
    print()

    a2 = Algebra('4-x+y-(3+x-y)')
    print('Case 2:', a2)
    print(a2.eval_str('x=4,y=2'))
    print(a2.eval_str('x=9,y=0'))
    print(a2.eval_str('x=-100'))
    print(a2.eval_str('y=-100'))
    print(a2.eval_str('a=4'))
    print()

    a3 = Algebra('z+x-x+y+y')
    print('Case 3:', a3)
    print(a3.eval_str('x=-11,z=0'))
    print(a3.eval_str('x=11,z=4'))
    print(a3.eval_str('y=-9,z=0'))
    print(a3.eval_str('y=9,z=13'))
    print()

    a4 = Algebra('-a-((b-c)-d)-((e-f)-(g-(h-(i-j))))')
    print('Case 4:', a4)
    print(a4.eval_str('a=10,b=9,c=8,d=7,e=6,f=5,g=4,h=3,i=2,j=1'))
    print(a4.eval_str('a=10,b=9,c=8,d=7'))
    print(a4.eval_str('a=10,c=8,e=6,g=4,i=2'))
    print(a4.eval_str('b=9,d=7,f=5,h=3,j=1'))
    print()

    a5 = Algebra('(x-x)+(y-y)')
    print('Case 5:', a5)
    print(a5.eval_str('x=0,y=0'))
    print(a5.eval_str('x=1,y=2'))
    print(a5.eval_str('z=10'))
    print()

    a6 = Algebra('123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+a+b+c+d+e-(v+w+x+y+z)+a+b+c+d+e-(v+w+x+y+z)+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+123456789+a+b+c+d+e-(v+w+x+y+z)+a+b+c+d+e-(v+w+x+y+z)')
    print('Case 6:', a6)
    print(a6.eval_str('x=0,y=0'))
    print(a6.eval_str('x=1,y=2'))
    print(a6.eval_str('z=10'))
    print(a6.eval_str('a=99,b=142,c=555,d=113,e=67,v=-123,w=-19,x=-99,y=-1234,z=-256'))
    print()

    a7 = Algebra('a*b*x+a*b*y')
    print('Case 7:', a7)
    print(a7.eval_str('a=1,b=2,x=5,y=10'))
    print(a7.eval_str('x=5,y=10'))
    print(a7.eval_str('x=5,y=-10'))
    print(a7.eval_str('a=10,b=-5'))
    print(a7.eval_str('b=-20'))
    print()

    a8 = Algebra('(x*a+y*b)*(a*b)')
    print('Case 8:', a8)
    print(a8.eval_str('a=1,b=2,x=5,y=10'))
    print(a8.eval_str('x=5,y=10'))
    print(a8.eval_str('x=5,y=-10'))
    print(a8.eval_str('a=10,b=-5'))
    print(a8.eval_str('b=-20'))
    print()

    a9 = Algebra('(a+b)*(c+d)*(e+f)')
    print('Case 9:', a9)
    print(a9.eval_str('a=1,b=2'))
    print(a9.eval_str('b=5,d=10,f=7'))
    print(a9.eval_str('c=-5,d=5,e=10'))
    print(a9.eval_str('b=-3,c=7,d=2,f=9'))
    print(a9.eval_str('z=0'))
    print()

    input_path = 'q2/input0.txt'
    with open(input_path, 'r') as f:
        lines = f.readlines()
        lines = [line[:-1] for line in lines]

    expression = lines[0]
    algebra = Algebra(expression)
    for param in lines[2:]:
        print(algebra.eval_str(param))
