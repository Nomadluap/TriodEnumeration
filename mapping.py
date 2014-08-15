'''
mapping.py - contains definitions of Point, Vertex, and Mapping classes
'''
from config import N, M, T

class Point(tuple):
    '''
    A class which abstracts a tuple. In basic usage, it is used simply to
    overload the __eq__ operator, so that tuple-based points handle the
    base point correctly.
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


class Vertex(Point):
    def __str__(self):
        return "v" + tuple(self).__str__()

    def __repr__(self):
        return "v" + tuple(self).__str__()


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

    def __call__(self, *args):
        '''
        Call the mapping as a function
        If a the argument is a Vertex, the codomain Vertex corresponding to
        that domain Vertex is returned.
        If the argument is a Point, the mappping is interpolated to return the
        result.
        If the mapping is called with two integers, it is assumed that those
        two integers form the definition of a Vertex.
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
                    #do point stuff here
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


