from ply import lex

# List of acceptable tokens in KSP SFS grammar
tokens = (
    'LBRACE',
    'RBRACE',
    'EQUAL',
    'VAR',
)

# Regular expression rules for above tokens
t_LBRACE = r'{'
t_RBRACE = r'}'
t_EQUAL = r'='
t_VAR = r'[a-zA-Z0-9\.]+'


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Whitespace is always meaningless, duh
t_ignore = '[ \t]+'

lexer = lex.lex()
