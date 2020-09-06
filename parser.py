import sys
from ply import yacc

# Load list of tokens supported in our language
from lexer import t_RBRACE, get_lexer, tokens  # noqa


OBJECT_EXPR = 'object'
ATTRIBUTE_EXPR = 'attribute'


def p_expression_object(p):
    '''object_statement : VAR LBRACE statements RBRACE object_statement
                        | empty'''
    if p[1] is None:
        return
    statement = (OBJECT_EXPR, p[1], p[3])
    if p[5] is not None:
        statement += (p[5], )
    p[0] = statement


def p_expression_statement_list(p):
    '''statements : variable_expression
                  | variable_expression statements
                  | variable_expression object_statement
                  | object_statement
                  | empty'''
    token_count = len(p)
    if token_count == 2:
        p[0] = p[1]
    else:
        if p[2][0] == ATTRIBUTE_EXPR:
            p[0] = (p[1], p[2])
        else:
            statement = p[2]
            if p[2][0] == OBJECT_EXPR:
                statement = (p[2], )
            p[0] = (p[1], ) + statement


def p_expression_assignment(p):
    'variable_expression : VAR ASSIGNMENT'
    p[0] = (ATTRIBUTE_EXPR, p[1], p[2])


def p_empty(p):
    'empty :'
    pass


# Error rule for syntax errors
def p_error(p):
    print(p)
    print("Syntax error in input!")
    sys.exit(1)


def get_parser():
    get_lexer()
    return yacc.yacc()
