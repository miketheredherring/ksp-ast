from ply import yacc

# Load list of tokens supported in our language
from lexer import tokens


OBJECT_EXPR = 'object'
ATTRIBUTE_EXPR = 'attribute'
EXPANSION_EXPR = 'expansion'


def p_expression_expr(p):
    'expression : VAR LBRACE expression RBRACE'
    p[0] = (OBJECT_EXPR, p[1], p[3])


def p_expression_equal(p):
    'expression : VAR EQUAL VAR'
    p[0] = (ATTRIBUTE_EXPR, p[1], p[3])


def p_expression_expansion(p):
    'expression : expression expression'
    p[0] = (EXPANSION_EXPR, p[1], p[2])


# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")


parser = yacc.yacc()
