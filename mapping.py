'''
mapping.py - contains definitions of Point, Vertex, and Mapping classes
'''
from config import N, M, T


class Point(tuple):
    '''
    A class which abstracts a tuple. 
    A point is defined as having an integer arm value and a floating-point dist
    value where:
    0<=arm<T
    0<=dist<=1
    '''
    def __init__(self, a, b=None):
        if b is not None:
            a = (a, b)
        tuple.__init__(self, a)

    def __new__(self, a, b=None):
        '''
        Redefinition of the tuple method so that points can be constructed
        as p(1, 2) as opposed to p((1, 2)).
        '''
        #apparently we need this because tuples are immutable.
        if b is not None:
            a = (a, b)
        return tuple.__new__(self, a)

    def __eq__(self, y):
        '''
        True if and only if x == y.
        Takes into account the three-definitions for the zero-point
        '''
        #additionally true iff both coords are at zero, regardless
        #of arm. 
        if type(self) is not type(y):
            raise ValueError('operands are of differing type')
        if self[1] == y[1] == 0:
            return True
        else:
            return tuple.__eq__(self, y)

    def __sub__(self, y):
        '''
        Defines subtraction between two Points such that the distance between
        two points is returned, using a railway metric. The result returned is
        always in absolute value.
        '''
        if type(self) is not type(y):
            raise ValueError('operands are of differing type')
        #if both points lie on the same arm, then use simple subtraction
        if self[0] == y[0]:
            return abs(self[1] - y[1])
        #otherwise return the sum of distances of each point from the center
        else:
            return self[1] + y[1]

    def __str__(self):
        '''for easy debugging'''
        return "p" + tuple(self).__str__()

    def __repr__(self):
        '''for easy debugging'''
        return "p" + tuple(self).__repr__()

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


class Vertex(Point):
    '''
    A class which abstracts a tuple. 
    A point is defined as having an integer arm value and a floating-point dist
    value where:
    0<=arm<T
    0<=dist<=N
    '''
    def __str__(self):
        return "v" + tuple(self).__str__()

    def __repr__(self):
        return "v" + tuple(self).__str__()

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
        if self.arm < 0 or self.arm >= T:
            return False
        #test distance
        if self.dist < 0 or self.dist > N:
            return False
        #otherwise good
        return True

    def isCodomain(self):
        '''
        Determine whether this vertex represents a valid point in the codomain.
        Returns True if the vertex lies in the domain
        '''
        #test leg number
        if self.arm < 0 or self.arm >= T:
            return False
        #test distance
        if self.dist < 0 or self.dist > M:
            return False
        #otherwise good
        return True


class Mapping(object):
    '''
    Mapping class represents a single mapping from a triod to a triod
    '''

    def __init__(self, mapList=None, basepoint=None, endpointMap=None):
        '''
        initalize in the following order:
        1. If a maplist is given, initialize to that maplist.
        2. If a basepoint is given, initialize to an empty mapping containing
        only that basepoint.
        3. If the endpointMap is supplied, save it as well.
        '''
        self._legs = []
        self.endpointMap = []
        self._basepoint = Vertex(0, 0)
        if mapList is not None:
            if type(mapList) is not list:
                raise ValueError("mapList must be a list")
            self._basepoint = mapList[0]
            self._legs = mapList[1:]
        elif basepoint is not None:
            #type-checking
            if type(basepoint) is not Vertex:
                raise ValueError("Basepoint must be of vertex type")
            self._basepoint = basepoint
            self._legs += ([list() for i in range(T)])
        else:
            self._legs += ([list() for i in range(T)])

        if endpointMap is not None:
            self.endpointMap = endpointMap
        #append the ends of leg lists to pad to proper lengths
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
            raise ValueError("Calling the mapping expects one or two values")
        if len(args) == 2:
            a, b = args
            #sanity checking
            if type(a) is not int or type(b) is not int:
                raise ValueError("Two arguments of type 'int' are expected")
            if a < 0 or a >= T:
                raise ValueError("First argument must lie in [0, T)")
            if b < 0 or b > N:
                raise ValueError("Second argument must lie in [0, N]")
            #do a dereference
            if b == 0:
                return self._basepoint
            else:
                return self._legs[a][b]

        if len(args) == 1:
            if type(args[0]) is Point:
                    point = args[0]
                    return self._mappingDereference(point)
            elif type(args[0]) is Vertex:
                vertex = args[0]
                if vertex == Vertex(0, 0):
                    return self._basepoint
                else:
                    return self._legs[vertex[0]][vertex[1]]
            else:
                raise ValueError("Argument must be of type 'Point' or type \
                'Vertex'")

    def __str__(self):
        s = "map[" + str(self._basepoint) + ", "
        for leg in self._legs:
            s += str(leg) + " "
        s += "]"
        return s

    def __repr__(self):
        return self.__str__()

    def getList(self):
        '''
        Returns the list representation of this mapping.
        '''
        l = [] + self._basepoint + self._legs
        return l

    def set(self, vertex, value):
        '''
        Set the value to which a particular vertex will dereference.
        set will throw a ValueError if continuity with ajacent points is not
        upheld.
        '''
        #type checking
        if type(vertex) is not Vertex or type(value) is not Vertex:
            raise ValueError('both arguments must be of type Vertex')
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

    def _mappingDereference(self, point):
        #point is in non-normalized tuple form
        arm, vertex = point
        #find nearest integers to vertex
        vLow = int(vertex)
        vHigh = int(vertex+1)
        if vHigh > N:  # gone past endpoint, therefore vertex is the endpoint
            vHigh = N
        #dereference vLow
        if vLow == 0:  # look at branchpoint
            fLow = self(0, 1)
        else:
            fLow = self(arm+1, vLow-1)[1]
        #dereference vHigh
        fHigh = self(arm+1, vHigh-1)[1]
        #find the arm that the new point now resides on
        fArm = self(arm+1, vHigh-1)[0]
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
