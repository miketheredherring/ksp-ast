import sys

from ply import lex

# List of acceptable tokens in KSP SFS grammar
tokens = (
    'LBRACE',
    'RBRACE',
    'ASSIGNMENT',
    'VAR',
)


def t_ASSIGNMENT(t):
    r'= [^\n]+'
    t.value = t.value[2:]
    return t


# Regular expression rules for above tokens
t_LBRACE = r'{'
t_RBRACE = r'}'


def t_VAR(t):
    r'[a-zA-Z0-9_/\. -]+'
    if t.value[-1] == ' ':
        t.value = t.value[:-1]
    return t


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Whitespace is always meaningless, duh
t_ignore = '[ \t]+'


# Error rule for token errors
def t_error(t):
    print(t)
    print("Token error in source!")
    sys.exit(2)


def get_lexer():
    return lex.lex()
