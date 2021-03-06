'''
mapping.py - contains definitions of Point, Vertex, and Mapping classes
'''
from config import N, M, T
from abc import ABCMeta


class AbstractPoint(tuple):
    '''
    An abstract base class which is used as the superclass for both Point and
    Vertex.
    '''
    __metaclass__ = ABCMeta

    def __new__(self, *args):
        '''
        Redefinition of the tuple method so that points can be constructed
        as p(1, 2) as opposed to p((1, 2)).
        '''
        if len(args) == 1:
            a = args[0]
#                raise TypeError("First arg must be of type {}".format(
#                    str(type(self))[7:-2]))
            return tuple.__new__(self, a)
        elif len(args) == 2:
            # subclasses should perform their own bounds checking
            arm, t = args
            if not isinstance(arm, int):
                raise TypeError("First argument must be of type 'int'")
            if not isinstance(t, (int, float)):
                raise TypeError("Second argument must be of type 'int' or\
                        'float'")
            if arm < 0:
                raise ValueError("First argument must be non-negative")
            if t < 0:
                raise ValueError("Second argument must be non-negative")
            #simplify arm
            if t == 0:
                arm = 0
            return tuple.__new__(self, (arm, t))
        else:
            raise TypeError("Constructor must be called with 1 or 2 arguments")

    def __eq__(self, y):
        '''
        True if and only if x == y.
        Takes into account the three-definitions for the zero-point
        '''
        #additionally true iff both coords are at zero, regardless
        #of arm.
        if type(self) is not type(y):
            raise TypeError('operands are of differing type')
        if self[1] == y[1] == 0:
            return True
        else:
            return tuple.__eq__(self, y)

    def __ne__(self, y):
        return not self.__eq__(y)

    def __sub__(self, y):
        '''
        Defines subtraction between two Points such that the distance between
        two points is returned, using a railway metric. The result returned is
        always in absolute value.
        '''
        if type(self) is not type(y):
            raise TypeError('operands are of differing type')
        #if both points lie on the same arm, then use simple subtraction
        if self[0] == y[0]:
            return abs(self[1] - y[1])
        #otherwise return the sum of distances of each point from the center
        else:
            return self[1] + y[1]

    def arm(self):
        '''
        Returns the arm of the current point
        '''
        return self[0]

    def dist(self):
        '''
        returns the distance of the current point up its arm
        '''
        return self[1]


class Point(AbstractPoint):
    '''
    A class which represents a triod point.
    A point is defined as having an integer arm value and a floating-point dist
    value where:
    0<=arm<T
    0<=dist<=1
    '''
    def __new__(self, *args):
        if len(args) == 2:
            arm, t = args
            if t < 0.0 or t > 1.0:
                raise ValueError("Second argument must be in range [0, 1]")
        return AbstractPoint.__new__(self, *args)

    def __str__(self):
        return "p" + tuple(self).__str__()

    def __repr__(self):
        return self.__str__()


class Vertex(AbstractPoint):
    '''
    A class which abstracts a tuple.
    A point is defined as having an integer arm value and a floating-point dist
    value where:
    0<=arm<T
    0<=dist<=N
    '''
    def __new__(self, *args):
        if len(args) == 2:
            arm, t = args
            if not isinstance(t, int):
                raise TypeError("Second argument must be of type 'int'.")
        return AbstractPoint.__new__(self, *args)

    def __str__(self):
        return "v" + tuple(self).__str__()

    def __repr__(self):
        return self.__str__()

    def _ajacent(self, i):
        '''
        Return a tuple of domain verticies which are ajacent to this point.
        Points will always be in a well-defined order, as follows:
        - the point itself
        - point(s) closer to the branch point
        - point(s) farther from the branch point
        If the point supplied is the
        branch point, then points will be supplied in order of decreasing
        index.
        '''
        arm, t = self
        #special case for the branch point
        if t == 0:
            return (Vertex(0, 0),) + tuple(Vertex(i, 1) for i in range(T))
        #endpoint condition
        elif t == i:
            return (self, Vertex(arm, t-1))
        else:
            return (self, Vertex(arm, t-1), Vertex(arm, t+1))

    def ajacentDomain(self):
        '''
        Return a tuple of domain verticies which are ajacent to this point.
        Points will always be in a well-defined order, as follows:
        - the point itself
        - point(s) closer to the branch point
        - point(s) farther from the branch point
        If the point supplied is the
        branch point, then points will be supplied in order of decreasing
        index.
        Returns None if the point is not on the domain.
        '''
        if not self.isDomain():
            return None
        return self._ajacent(N)

    def ajacentCodomain(self):
        '''
        Return a tuple of codomain verticies which are ajacent to this point.
        Points will always be in a well-defined order, as follows:
        - the point itself
        - point(s) closer to the branch point
        - point(s) farther from the branch point
        If the point supplied is the
        branch point, then points will be supplied in order of decreasing
        index.
        Returns None if the point is not on the codomain.
        '''
        if not self.isCodomain():
            return None
        return self._ajacent(M)

    def isDomain(self):
        '''
        Determine whether this vertex represents a valid point in the domain.
        Returns True if the vertex lies in the domain
        '''
        #test leg number
        if self.arm() < 0 or self.arm() >= T:
            return False
        #test distance
        if self.dist() < 0 or self.dist() > N:
            return False
        #otherwise good
        return True

    def isCodomain(self):
        '''
        Determine whether this vertex represents a valid point in the codomain.
        Returns True if the vertex lies in the domain
        '''
        #test leg number
        if self.arm() < 0 or self.arm() >= T:
            return False
        #test distance
        if self.dist() < 0 or self.dist() > M:
            return False
        #otherwise good
        return True

    def toward(self, v):
        '''
        Return the vertex q such that (v-q) == (self-q) -1, or None if v ==
        self.
        '''
        if not isinstance(v, Vertex):
            raise TypeError("v must be of type 'Vertex'")
        # if we are v, return None
        if self == v:
            return None
        # if we are the branch point, simply go down the proper leg
        if self == Vertex(0, 0):
            return Vertex(v[0], 1)
        # if we are on different legs, go toward the endpoint
        if self[0] != v[0]:
            return Vertex(self[0], self[1]-1)
        # if v is toward branch point, go that way
        if v[1] < self[1]:
            return Vertex(self[0], self[1]-1)
        else:
            return Vertex(self[0], self[1]+1)


class Mapping(object):
    '''
    Mapping class represents a single mapping from a triod to a triod
    '''
    _legs = []
    endpointMap = []
    _basepoint = Vertex(0, 0)
    idnum = 0  # used for identification in empty generators.

    def __init__(self, a):
        '''
        Initialize in the following way:
        - If a is None, an empty mapping with basepoint at v(0, 0) will be
          created.
        - If a is of type 'Vertex', create an empty mapping with that vertex at
          the basepoint
        - If a is of type 'Mapping', construct a copy of that mapping.
        - If a ls of type 'list', create the mapping described by that list. If
          the argument is of this type, the list must be of the following form:
          1. The first element must be of type 'Vertex'
          2. The consecutive elements must be lists containing values of type
          'Vertex' or None. 
          3. The list will only be parsed until the mapping has bounds which
          correspond to N, M, and T in config.py.
        '''
        # first initialize empty legs
        self._legs = [list() for i in range(T)]
        # populate based on argument
        if a is None:
            pass
        elif isinstance(a, Vertex):
            # Vertex must lie in codomain
            if not a.isCodomain():
                raise ValueError('Vertex {} is not in codomain.'.format(a))
            self._basepoint = a
        elif isinstance(a, Mapping):
            # perform a deep copy
            self._basepoint = a._basepoint
            self.id = a.id
            self.endpointMap = list(a.endpointMap)
            for i in range(T):
                self._legs[i] = list(a._legs[i])
        elif isinstance(a, list):
            # verify list structure
            if not isinstance(a[0], Vertex):
                raise TypeError("First element of list must be 'Vertex' type.")
            if not a[0].isCodomain():
                raise ValueError('Vertex {} is not in codomain.'.format(a))
            for leg in a[1:T+1]:
                if type(leg) is not list:
                    raise TypeError("Remaining elements of list must be type \
'list'")
                for v in leg:
                    if not (isinstance(v, Vertex) or v is None):
                        raise TypeError("Sublist elements must be type \
'Vertex'")
                    # Verify bounds of each vertex.
                    if v is not None and not v.isCodomain():
                        raise ValueError("Vertex {} is not in codomain."
                                         .format(v))
            # list is good, unpack
            self._basepoint = a[0]
            for i in range(T):
                self._legs[i] = list(a[i+1])
        else:
            raise TypeError("Argument of wrong type")
        # and now pack the lists
        self._pad_lists()

    def _pad_lists(self):
        '''
        pad the entries in _legs so that they are all of the proper size.  This
        should be done after every mapping update.
        '''
        for leg in self._legs:
            while len(leg) < N:
                leg.append(None)

    def __call__(self, *args):
        '''
        Call the mapping as a function
        If a the argument is a Vertex, the codomain Vertex corresponding to
        that domain Vertex is returned.
        If the argument is a Point, the mappping is interpolated to return the
        result.
        If the mapping is called with two integers, it is assumed that those
        two integers form the definition of a Vertex.

        If the mapping is undefined at the point specified, a value of None is
        returned.
        '''
        if len(args) not in (1, 2):
            raise TypeError("Calling the mapping expects one or two values")
        if len(args) == 2:
            a, b = args
            #sanity checking
            if type(a) is not int or type(b) is not int:
                raise TypeError("Two arguments of type 'int' are expected")
            if a < 0 or a >= T:
                raise ValueError("First argument must lie in [0, T)")
            if b < 0 or b > N:
                raise ValueError("Second argument must lie in [0, N]")
            #do a dereference
            if b == 0:
                return self._basepoint
            else:
                return self._legs[a][b-1]

        if len(args) == 1:
            if type(args[0]) is Point:
                    point = args[0]
                    return self._mappingDereference(point)
            elif type(args[0]) is Vertex:
                vertex = args[0]
                if vertex == Vertex(0, 0):
                    return self._basepoint
                else:
                    return self._legs[vertex[0]][vertex[1]-1]
            else:
                raise TypeError("Argument must be of type 'Point' or type \
                'Vertex'")

    def __str__(self):
        s = "map[" + str(self._basepoint)
        for leg in self._legs:
            s += ", " + str(leg)
        s += " ]"
        return s

    def __repr__(self):
        return self.__str__()

    def getList(self):
        '''
        Returns the list representation of this mapping.
        '''
        l = [] + self._basepoint + self._legs
        return l

    def getLeg(self, n):
        '''
        Returns a list representing leg number N of the mapping, not including
        the base point.
        '''
        if n < 0 or n >= T:
            raise ValueError("n is out of range")
        return self._legs[n]

    def set(self, vertex, value):
        '''
        Set the value to which a particular vertex will dereference.
        set will throw a ValueError if continuity with ajacent points is not
        upheld.
        '''
        #type checking
        if type(vertex) is not Vertex or type(value) is not Vertex:
            raise TypeError('both arguments must be of type Vertex')
        if not vertex.isDomain():
            raise ValueError('vertex argument must lie in domain')
        if not value.isCodomain():
            raise ValueError('vertex argument must lie in domain')
        #special case for base point
        if vertex == Vertex(0, 0):
            #check that new point satisfies continuity for all legs.
            for leg in self._legs:
                if leg[0] is None:
                    continue
                if value not in leg[0].ajacentCodomain():
                    raise ValueError("Point would not satisfy continuity\
                            with point: {}".format(str(leg[0])))
            #if valueError has not been raised, we're good
            self._basepoint = value
        else:
            #make sure value we're trying to set is ajacent to values of
            #neibhouring points, if they are defined.
            for p in vertex.ajacentDomain():
                #dereference p
                fp = self(p)
                if fp is None:
                    continue
                #ensure this point is in the ajacent set of the value we're
                #trying to set.
                if fp not in value.ajacentCodomain():
                    raise ValueError('Ajacent vertex {} -> {} causes\
                        discontinuity'.format(str(p), str(fp)))
            #otherwise we're good
            self._legs[vertex.arm][vertex.dist] = value
            self._pad_lists()

    def _mappingDereference(self, point):
        #point is in non-normalized tuple form
        arm, vertex = point
        #find nearest integers to vertex
        vLow = int(vertex)
        vHigh = int(vertex+1)
        if vHigh > N:  # gone past endpoint, therefore vertex is the endpoint
            vHigh = N
        try:
            #dereference vLow
            if vLow == 0:  # look at branchpoint
                fLow = self(0, 0)[1]
            else:
                fLow = self(arm, vLow-1)[1]
            #dereference vHigh
            fHigh = self(arm, vHigh-1)[1]
            #find the arm that the new point now resides on
            fArm = self(arm, vHigh-1)[0]
        except TypeError:
            return None
        #decimal portion of vertex indicates where it lies between fLow and
        #fHigh.
        vP = vertex % 1.0
        #now go uP distance from fLow to fHigh. If order of fHigh, fLow is
        #reversed, then we need to subtract rather than add.
        if fLow < fHigh:
            f = fLow + vP
        elif fLow == fHigh:
            f = fLow
        else:
            f = fLow - vP
        #the zero point should always lie on the zero-arm for testing purposes.
        if f == 0:
            fArm = 0
        return Point(fArm, f)


class MappingPair(object):
    '''A class which represents a pair of mappings, and its assosciated id'''
    idnum = 0
    map1 = None
    map2 = None

    def __init__(self, *args):  # :idnum, map1, map2):
        '''
        MappingPair(idnum, map1, map2) -> new MappingPair object
        MappingPair(map1, map2) -> new MappignPair object
        MappingPair(p) -> Copy of existing MappingPair object
        '''
        if len(args) == 3:
            self.idnum = args[0]
            self.map1 = args[1]
            self.map2 = args[2]
        elif len(args) == 1:
            o = args[0]
            if type(o) is not type(self):
                raise TypeError("ASDFFADF")
            print type(o)
            self.idnum = o.idnum
            self.map1 = o[0]
            self.map2 = o[1]
        elif len(args) == 2:
            self.idnum = -1
            self.map1 = args[0]
            self.map2 = args[1]
        else:
            raise TypeError("Bad number of arguments")

        if not (isinstance(self.map1, Mapping) and isinstance(self.map2,
                Mapping)):
            raise TypeError("Map1 and Map2 must be of type 'Mapping'")

    def __getitem__(self, key):
        if key == 0:
            return self.map1
        elif key == 1:
            return self.map2
        else:
            raise IndexError("Index out of range")

    def __str__(self):
        return "id: {} {{{} , {}}}".format(self.idnum, self.map1, self.map2)

    def __repr__(self):
        return self.__str__()
