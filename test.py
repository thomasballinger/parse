import re

# shims for Python 2
import sys
if sys.version_info[0] == 2:
    input = raw_input


class Tokens():
    def __init__(self, s):
        self.tokens = tokenize(s)
        self.current_i = 0
    def peek(self):
        return self.tokens[self.current_i]
    def consume(self):
        t = self.tokens[self.current_i]
        self.current_i += 1
        return t

def tokenize(s):
    """
    >>> tokenize("(1.1 + 2 * 3)")
    ['(', '1.1', '+', '2', '*', '3', ')']
    """
    return re.findall("[0123456789.]+|[*+/\-()]", s)

"""
Exp E -> T | T+E | T-E
Term T -> P | P*T | P/T
Phrase P -> number | (E) | -number | -(E)

1 + 2 * 3 + 1
"""

def expression(tokens):
    """
    >>> expression(['1'])
    ('1', [])
    >>> expression(['1', '*', '2'])
    (['*', '1', '2'], [])
    >>> expression(['1', '+', '2'])
    (['+', '1', '2'], [])
    >>> expression(tokenize('1+2*3'))
    (['+', '1', ['*', '2', '3']], [])
    """
    t, rest_of_tokens = term(tokens)
    if len(rest_of_tokens) == 0:
        return t, rest_of_tokens
    else:
        token = rest_of_tokens[0]
        if token in ['-', '+']:
            rest_of_tokens.pop(0)
            exp, rest_of_tokens = expression(rest_of_tokens)
            return [token, t, exp], rest_of_tokens
        else:
            return t, rest_of_tokens

def term(tokens):
    """Term T -> P | P*T | P/T

    >>> term(['1.2', '*', '123'])
    (['*', '1.2', '123'], [])
    >>> term(['1.2'])
    ('1.2', [])
    >>> term(['1', '+', '2'])
    ('1', ['+', '2'])
    """
    phra, rest_of_tokens = phrase(tokens)
    if len(rest_of_tokens) == 0:
        return phra, rest_of_tokens
    else:
        token = rest_of_tokens[0]
        if token in ['*', '/']:
            rest_of_tokens.pop(0)
            t, rest_of_tokens = term(rest_of_tokens)
            return [token, phra, t], rest_of_tokens
        else:
            return phra, rest_of_tokens

def is_numeric(s):
    """
    >>> is_numeric('1')
    True
    """
    return all(l in '1234567890.' for l in s)

def phrase(tokens):
    """
    >>> phrase(['1'])
    ('1', [])
    >>> phrase(['1.213'])
    ('1.213', [])
    >>> phrase(tokenize('(1)'))
    ('1', [])
    """

    t = tokens.pop(0)
    if is_numeric(t):
        return t, tokens
    elif t == '(':
        e, rest_of_tokens = expression(tokens)
        t = rest_of_tokens.pop(0)
        if t != ')':
            raise SyntaxError('whoops')
        return e, rest_of_tokens
    else:
        assert False, 'uh oh, t was actually %r' % t

def gen_python_code(tree):
    ops = {'+':'__import__("operator").add',
           '-':'__import__("operator").sub',
           '*':'__import__("operator").mul',
           '/':'__import__("operator").div'}
    if isinstance(tree, list):
        operator, operand1, operand2 = tree
        return '__import__("functools").reduce(%s, [%s, %s])' % (ops[operator], gen_python_code(operand1), gen_python_code(operand2))
    else:
        return tree

def gen_short_python_code(tree):
    if isinstance(tree, list):
        operator, operand1, operand2 = tree
        return '(%s %s %s)' % (gen_short_python_code(operand1), operator, gen_short_python_code(operand2))
    else:
        return tree

if __name__ == '__main__':
    import doctest
    import pprint
    doctest.testmod()
    s = '1+4*3-(2*4-3+(1+1))*8'
    print(s)
    print(tokenize('1+4*3-(2*4-3+(1+1))*8'))
    print(expression(tokenize('1+4*3-(2*4-3+(1+1))*8')))
    pprint.pprint(expression(tokenize('1+4*3-(2*4-3+(1+1))*8')))
    s = input('type an expression: ')
    code = gen_python_code(expression(tokenize(s))[0])
    print(code)
    print(eval(code))
    code = gen_short_python_code(expression(tokenize(s))[0])
    print(code)
    print(eval(code))
