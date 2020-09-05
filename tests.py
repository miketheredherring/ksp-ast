from unittest import TestCase

from ply.lex import LexToken as InternalLexToken

from parser import (
    OBJECT_EXPR, ATTRIBUTE_EXPR, EXPANSION_EXPR,
    parser
)
from lexer import lexer


class LexToken(InternalLexToken):
    def __init__(self, obj, value, lineno, pos):
        super().__init__()
        self.type = obj
        self.value = value
        self.lineno = lineno
        self.lexpos = pos

    def __eq__(self, other):
        return (
            self.type == other.type and
            self.value == other.value and
            self.lineno == other.lineno and
            self.lexpos == other.lexpos
        )


class ParserTests(TestCase):
    def test_lex_game_only(self):
        '''Ensures we can lex the most basic file.
        '''
        with open('data/01_test.sfs', 'r') as f:
            data = f.read()
            lexer.input(data)

        tokens = []
        while True:
            token = lexer.token()
            if not token:
                break
            tokens.append(token)

        self.assertSequenceEqual(
            tokens,
            [
                LexToken('VAR', 'GAME', 1, 0),
                LexToken('LBRACE', '{', 2, 5),
                LexToken('VAR', 'version', 3, 11),
                LexToken('ASSIGNMENT', '1.10.1', 3, 19),
                LexToken('VAR', 'Title', 4, 32),
                LexToken('ASSIGNMENT', 'LunaMultiplayer', 4, 38),
                LexToken('RBRACE', '}', 5, 56)
            ]
        )

    def test_parse_game_only(self):
        '''Ensures we can parse the most basic file.
        '''
        with open('data/01_test.sfs', 'r') as f:
            data = f.read()

        result = parser.parse(data)
        self.assertEqual(
            result,
            (
                OBJECT_EXPR, 'GAME',
                (
                    (ATTRIBUTE_EXPR, 'version', '1.10.1'),
                    (ATTRIBUTE_EXPR, 'Title', 'LunaMultiplayer'),
                )
            )
        )

    def test_parse_nested(self):
        '''Ensures we can parse nested objects with multiple statements.
        '''
        with open('data/02_test_nested.sfs', 'r') as f:
            data = f.read()

        result = parser.parse(data)
        self.assertEqual(
            result,
            (
                OBJECT_EXPR, 'GAME',
                (
                    (ATTRIBUTE_EXPR, 'version', '1.10.1'),
                    (ATTRIBUTE_EXPR, 'Title', 'LunaMultiplayer'),
                    (ATTRIBUTE_EXPR, 'Seed', '553334321'),
                    OBJECT_EXPR, 'PARAMETERS',
                    (
                        (ATTRIBUTE_EXPR, 'preset', 'Custom'),
                        OBJECT_EXPR, 'FLIGHT',
                        (
                            (ATTRIBUTE_EXPR, 'CanQuickSave', 'True'),
                            (ATTRIBUTE_EXPR, 'CanLeaveToMainMenu', 'True'),
                        )
                    )
                )
            )
        )

    def test_parse_complex(self):
        '''Ensures we can parse a real game file.
        '''
        with open('data/persistent.sfs', 'r') as f:
            data = f.read()
            parser.parse(data)
