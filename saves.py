from parser import (
    ATTRIBUTE_EXPR, OBJECT_EXPR,
    get_parser
)


class Part(object):
    object_id = 'PART'

    # Constants identifying common parts
    DOCKING_PORT = 'ModuleDockingNode'

    def __init__(self, name=None, MODULE=None, **kwargs):
        self.name = name
        self.module = MODULE

    def __repr__(self):
        return self.name

    @classmethod
    def bind(cls, **kwargs):
        '''Generate either generic or specific part class.
        '''
        module = kwargs.get('MODULE', None)
        if module is not None:
            module_attributes = KerbalAST.get_attributes_as_dict(
                (OBJECT_EXPR, 'MODULE', module)
            )
            if module_attributes['name'] == Part.DOCKING_PORT:
                return DockingPort(
                    module_attributes,
                    **kwargs
                )
        return Part(**kwargs)


class DockingPort(Part):
    # Constants identifying potential states
    STATE_READY = 'Ready'

    def __init__(self, mod_attrs, rTrf=None, **kwargs):
        super().__init__(**kwargs)

        # Parse component specific state
        self.dock_id = mod_attrs['dockUId']
        self.is_enabled = mod_attrs['isEnabled']
        self.state = mod_attrs['state']
        self.reference_type = rTrf

        # Parse out docked vessel
        self.docked_vessel = mod_attrs.get('DOCKEDVESSEL', None)
        if self.docked_vessel is not None:
            self.docked_vessel = KerbalAST.get_attributes_as_dict(
                (OBJECT_EXPR, 'DOCKEDVESSEL', self.docked_vessel)
            )

    def __repr__(self):
        ret = '<%s %s : %s>' % (self.reference_type.title(), self.dock_id, self.state)
        if self.docked_vessel:
            ret += ' - %s' % (self.docked_vessel['vesselName'])
        return ret


class Vessel(object):
    object_id = 'VESSEL'

    # Constants for identifying types of vessels
    TYPE_BASE = 'Base'
    TYPE_FLAG = 'Flag'
    TYPE_LANDER = 'Lander'
    TYPE_RELAY = 'Relay'
    TYPE_SPACE_OBJECT = 'SpaceObject'
    TYPE_STATION = 'Station'

    def __init__(self, name=None, persistentId=None, type=None, **kwargs):
        self.name = name
        self.type = type
        self.persistent_id = persistentId
        self.parts = []

    def get_docking_ports(self):
        ports = []
        for part in self.parts:
            if isinstance(part, DockingPort):
                ports.append(part)
        return ports

    def validate_docks(self, expected_vessels=None):
        '''Validates all ports are properly docked and not orphaned.

        When providing `expected_vessels` we can identify orphaned
        docks more reliably since missing references can be suggested
        based on orientation/positions of the ports.
        '''
        pairs = []
        for port in self.get_docking_ports():
            pass

    def __repr__(self):
        return '<Vessel %s (%s %s)>' % (self.name, self.type, self.persistent_id)


class KerbalAST(object):
    '''In-memory representation for KSP SFS file.

    The goal of this class to to be able to introspect
    and search a given game state to find potential errors,
    fix them, or visualize your data.
    '''

    def __init__(self, filename):
        '''Loads the file into an AST and indexes important structures.
        '''
        self.vessels = []
        self.ast = None
        self.load_ast_from_file(filename)

    def get_vessels(self, _type=None):
        '''Filter all vessels that match the search criteria.
        '''
        for vessel in self.vessels:
            if (
                _type is None or
                _type == vessel.type
            ):
                yield vessel

    @staticmethod
    def get_attributes_as_dict(obj):
        attributes = {}
        for attr in obj[2]:
            attributes[attr[1]] = attr[2]
        return attributes

    def load_ast_from_file(self, filename):
        '''Build the poor mans AST from our SFS parser.
        '''
        parser = get_parser()
        with open(filename, 'r') as f:
            data = f.read()
            self.ast = parser.parse(data)

    def translate_ast_to_native(self):
        '''Convert the AST into a data index with Python native structures (dict/class).
        '''
        if self.ast is None:
            raise RuntimeError('You must load and AST prior to indexing')
        self.process_subtree(self.ast)

    def process_subtree(self, current_ast):
        '''Inspect the current node of the AST and recurse or complete serializing.
        '''
        if current_ast is None:
            return

        # If we can inspect or recurse
        if current_ast[0] == OBJECT_EXPR:
            if current_ast[1] == Vessel.object_id:
                vessel = Vessel(
                    **KerbalAST.get_attributes_as_dict(current_ast)
                )

                for sub_elem in current_ast[2]:
                    if sub_elem[0] == OBJECT_EXPR:
                        if sub_elem[1] == Part.object_id:
                            part = Part.bind(
                                **KerbalAST.get_attributes_as_dict(sub_elem)
                            )
                            vessel.parts.append(part)
                self.vessels.append(vessel)
            else:
                children = current_ast[2]
                if children:
                    for sub_elem in children:
                        if sub_elem[0] != ATTRIBUTE_EXPR:
                            self.process_subtree(sub_elem)
