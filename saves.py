from ply import lex


class KerbalAST(object):
    '''In-memory representation for KSP SFS file.

    The goal of this class to to be able to introspect
    and search a given game state to find potential errors,
    fix them, or visualize your data.
    '''