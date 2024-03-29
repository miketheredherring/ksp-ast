from unittest import TestCase

from ply.lex import LexToken as InternalLexToken

from lexer import get_lexer
from parser import (
    OBJECT_EXPR, ATTRIBUTE_EXPR,
    get_parser
)
from saves import KerbalAST, Vessel


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
        lexer = get_lexer()
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

        parser = get_parser()
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

        parser = get_parser()
        result = parser.parse(data)
        self.assertEqual(
            result,
            (
                OBJECT_EXPR, 'GAME',
                (
                    (ATTRIBUTE_EXPR, 'version', '1.10.1'),
                    (ATTRIBUTE_EXPR, 'Title', 'LunaMultiplayer'),
                    (ATTRIBUTE_EXPR, 'Seed', '553334321'),
                    (
                        OBJECT_EXPR, 'CometNames', ()
                    ),
                    (
                        OBJECT_EXPR, 'PARAMETERS',
                        (
                            (ATTRIBUTE_EXPR, 'preset', 'Custom'),
                            (
                                OBJECT_EXPR, 'FLIGHT',
                                (
                                    (ATTRIBUTE_EXPR, 'CanQuickSave', 'True'),
                                    (ATTRIBUTE_EXPR, 'CanLeaveToMainMenu', 'True'),
                                )
                            )
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
            parser = get_parser()
            parser.parse(data)

    def test_ast_get_vessels(self):
        '''Ensures we can parse a real game file into and AST and extract vessels.
        '''
        ksp_universe = KerbalAST('data/persistent.sfs')
        ksp_universe.translate_ast_to_native()
        self.assertGreater(len(ksp_universe.vessels), 0)
        for vessel in ksp_universe.get_vessels(_type=Vessel.TYPE_BASE):
            print(str(vessel))
            for port in vessel.docking_ports:
                print('%s - %s' % (type(port), port))

    def test_ast_vessel_repair_docking_ports(self):
        '''Ensures we can parse a real vessel and find validation issues.
        '''
        ksp_universe = KerbalAST('data/03_docking.sfs')
        ksp_universe.translate_ast_to_native()
        self.assertEqual(len(ksp_universe.vessels), 1)
        for vessel in ksp_universe.get_vessels(_type=Vessel.TYPE_BASE):
            vessel.repair_docking_ports()
