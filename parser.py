from ply import yacc

# Load list of tokens supported in our language
from lexer import tokens


OBJECT_EXPR = 'object'
ATTRIBUTE_EXPR = 'attribute'
EXPANSION_EXPR = 'expansion'


def p_expression_expr(p):
    'expression : VAR LBRACE expression RBRACE'
    p[0] = (OBJECT_EXPR, p[1], p[3])


def p_expression_variable_expansion(p):
    '''expression : variable_expression
                  | variable_expression expression'''

    token_count = len(p)
    if token_count == 2:
        p[0] = p[1]
    else:
        if p[2][0] == ATTRIBUTE_EXPR:
            p[0] = (p[1], p[2])
        else:
            p[0] = (p[1], ) + p[2]


def p_expression_equal(p):
    'variable_expression : VAR EQUAL VAR'
    p[0] = (ATTRIBUTE_EXPR, p[1], p[3])


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()
