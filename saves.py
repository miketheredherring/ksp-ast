from copy import deepcopy

from exceptions import ValidationError
from parser import (
    ATTRIBUTE_EXPR, OBJECT_EXPR,
    get_parser
)


class Part(object):
    '''Generic `Part` representing anything you can make a rocket with in 1.11.X.

    All sub-classes of `Part` should take at least a single positional argument
    of `mod_attrs`, which is the parsed MODULE object belonging to the PART
    identifying itself. Since the MODULE object can be define multiple times,
    this one is the most relevant to a given PART and is passed as a convenience.

    The only reason something should parse as this class is because we have not
    had a need to inspect it further. Ideally all parts should be defined in a
    similar fashion to `DOCKING_PORT` by identifying a PART by its MODULE.

    Below is a list of the fields you may find on a PART object and my
    interpretation of what it is/should be used for; full disclaimer that these
    are best guesses, so please leave a comment if you know better than I :).

    `uid` - Unique ID given to every PART object in the game. Often used as a
        reference in other PART objects for connections like in docking.

    `mid` - Mission ID given for each launch in the game, all PART objects for
        a given rocket should be the same, easy way to identify all the PART
        objects belonging to a particular sub-vessel in a docked VESSEL object.

    `name` - Name given to a part. Some parts can be renamed in game and this will
        be the same, except for parts where you cannot provide a name, it will be
        something generic like `dockingPort1` for a docking port.

    `parent` - ID (or index) of PART in the VESSEL object for describing which
        PART objects are attached to each other permenantly. Often seen in the
        `attN` and `srfN` attributes for part orientation.

    `position` - Local X, Y, Z coordinates of the PART relative to the origin
        position of the VESSEL object.
    '''
    object_id = 'PART'

    # Constants identifying common parts
    DOCKING_PORT = 'ModuleDockingNode'
    VALID_MODULES = [DOCKING_PORT, ]

    def __init__(
        self,
        uid=None, mid=None,
        name=None, MODULE=None, parent=None, position=None,
        **kwargs
    ):
        '''Default values matching attribute definitions in PART object.
        '''
        self.unique_id = uid
        self.mission_id = mid
        self.name = name
        self.parent = parent
        self.modules = MODULE
        self.position = tuple(map(float, position.split(',')))

    def __repr__(self):
        return self.name

    @classmethod
    def bind(cls, **kwargs):
        '''Generate an instance of `Part` or a sub-class based on the provided MODULE object.
        '''
        part_cls = Part
        modules = kwargs.get('MODULE', None)
        mod_attrs = None
        if modules is not None:
            # Since we can get multiple modules, find the one that will determine the part
            if not isinstance(modules, list):
                modules = [modules, ]

            # Find the most relevant MODULE object for identifying this PART
            for module in modules:
                mod_attrs = KerbalAST.get_attributes_as_dict(
                    (OBJECT_EXPR, 'MODULE', module)
                )
                if mod_attrs['name'] == Part.DOCKING_PORT:
                    part_cls = DockingPort
                    break

        # Build args list from parsed attributes
        args = []
        if mod_attrs is not None:
            args = [mod_attrs, ]
        return part_cls(*args, **kwargs)

    def validate(self):
        '''Stub which will always pass validation.
        '''
        pass


class DockingPort(Part):
    # Constants identifying potential states
    STATE_READY = 'Ready'

    ROLE_DOCKER = 'docker'
    ROLE_DOCKEE = 'dockee'
    ROLES = [
        ROLE_DOCKER, ROLE_DOCKEE
    ]

    def __init__(self, mod_attrs, rTrf=None, **kwargs):
        super().__init__(**kwargs)

        # Parse component specific state
        self.docked_unique_id = mod_attrs['dockUId']
        self.is_enabled = mod_attrs['isEnabled']
        self.state = mod_attrs['state']
        self.reference_type = rTrf
        self.role = None

        # Identify if the port is the primary vehicle or the secondary
        for role in DockingPort.ROLES:
            if role in self.state:
                self.role = role
                break

        # Parse out docked vessel
        self.docked_vessel = mod_attrs.get('DOCKEDVESSEL', None)
        if self.docked_vessel is not None:
            self.docked_vessel = KerbalAST.get_attributes_as_dict(
                (OBJECT_EXPR, 'DOCKEDVESSEL', self.docked_vessel)
            )

    def __repr__(self):
        ret = '<%s %s : %s>' % (self.reference_type.title(), self.docked_unique_id, self.state)
        if self.docked_vessel:
            ret += ' - %s' % (self.docked_vessel['vesselName'])
        return ret

    def check_docked(self, other_port):
        '''Determine if there is an error in how two ports are docked.

            1. Validate `dockUId` matches `uid`
            2. Validate state is `Docked (docker|dockee)
        '''
        if self.unique_id != other_port.docked_unique_id:
            print('%s is missing `dockUId = %s`' % (other_port, self.unique_id))
        elif other_port.docked_unique_id != self.unique_id:
            print('%s is missing `dockUId = %s`' % (self, other_port.unique_id))

        # Check one vehicle is the primary and the other is the secondary
        roles = deepcopy(DockingPort.ROLES)
        try:
            roles.remove(self.role)
            roles.remove(other_port.role)
        except ValueError:
            print(
                '%s and %s have not properly identified primary secondary roles' % (
                    self, other_port
                )
            )

    def distance_to(self, other_port):
        '''Determine physical distance of ports from one another.
        '''
        return abs(
            (self.position[0] - other_port.position[0]) +
            (self.position[1] - other_port.position[1]) +
            (self.position[2] - other_port.position[2])
        )

    def validate(self):
        '''Identify all invalid states, assuming we are not in one, then we validated!
        '''
        if self.state == DockingPort.STATE_READY:
            if self.docked_vessel is not None:
                raise ValidationError(
                    'Docking port %s state is unbound, but has docked vessel' % (
                        self.docked_unique_id
                    )
                )


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

    @property
    def docking_ports(self):
        return list(filter(lambda p: isinstance(p, DockingPort), self.parts))

    def repair_docking_ports(self):
        ports = self.docking_ports
        print(ports)
        try:
            for port in ports:
                port.validate()
        except ValidationError:
            print('Docking port found in invalid config, attempting repair')

            # Order the ports by position and compare neighbors for likely mates
            ordered_ports = sorted(ports, key=lambda p: p.position)
            for idx, port in enumerate(ordered_ports[:-1]):
                neighbor = ordered_ports[idx + 1]

                # If the ports seem aligned, inspect they are matched
                if port.distance_to(neighbor) < 1.0:
                    print('Likely pair found: %s and %s' % (
                        port, neighbor
                    ))
                    port.check_docked(neighbor)

    def validate(self, expected_vessels=None):
        '''Validates all ports are properly docked and not orphaned.

        When providing `expected_vessels` we can identify orphaned
        docks more reliably since missing references can be suggested
        based on orientation/positions of the ports.
        '''
        for part in self.parts:
            part.validate()

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
            # Same key can occur multiple times
            if attr[1] in attributes:
                if not isinstance(attributes[attr[1]], list):
                    attributes[attr[1]] = [attributes[attr[1]], ]
                attributes[attr[1]].append(attr[2])
            else:
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

        # Ensure the current level is and object before inspecting
        if current_ast[0] == OBJECT_EXPR:
            if current_ast[1] == Vessel.object_id:
                vessel = Vessel(
                    **KerbalAST.get_attributes_as_dict(current_ast)
                )

                # Parse out individual parts for our `Vessel`
                for sub_elem in current_ast[2]:
                    if sub_elem[0] == OBJECT_EXPR:
                        if sub_elem[1] == Part.object_id:
                            part = Part.bind(
                                **KerbalAST.get_attributes_as_dict(sub_elem)
                            )
                            vessel.parts.append(part)
                self.vessels.append(vessel)
            else:
                # Process all the sub-objects recursively
                children = current_ast[2]
                if children:
                    for sub_elem in children:
                        if sub_elem[0] != ATTRIBUTE_EXPR:
                            self.process_subtree(sub_elem)
