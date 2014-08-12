'''
mapping.py - contains definitions of Point, Vertex, and Mapping classes
'''

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
    v
