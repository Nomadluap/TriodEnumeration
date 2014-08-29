'''
Comparitors.py - Functions to compare two triod mappings.
'''
from __future__ import division
from mapping import Vertex, Mapping, Point
from config import N, M, T


def checkDisjointness(partialMap1, partialMap2):
    '''
    Compares two partial mappings to determine if the mappings are properly
    disjoint. 

    If either mapping is only partially defined, disjointness will only be
    calculated for the domain vertices which are defined in both mappings.

    checkDisjointness returns the closest distance between mappings. If the
    mappings are not disjoint, this value will be 0.
    '''
    if not isinstance(partialMap1, Mapping):
        raise TypeError("Argument 1 must be of type 'Mapping'")
    if not isinstance(partialMap2, Maping):
        raise TypeError("Argument 2 must be of type 'Mapping'")

    # if mappings share a basepoint, we have a failure.
    baseA = partialMap1(0, 0)
    baseB = partialMap2(0, 0)
    if baseA == baseB:
        return 0
    dist = -1

    for arm in range(T):
        curA = baseA
        curB = baseB
        prevA = baseA
        prevB = baseB
        for t in range(0, N+1):
            curA = partialMap1(arm, t)
            curB = partialMap2(arm, t)
            # break if we reach an undefined portion of either mapping
            if curA is None or curB is None:
                break
            # if mappings co-incide
            if curA == curB:
                return 0
            # if mappings cross eachother
            elif curA == prevB and curB == prevA:
                return 0
            else:
                d = curA - curB
                if d < dist or dist == -1:
                    dist = d
            # and prepare for next iteration
            prevA = curA
            prevB = curB
        # if we haven't returned already, then we are properly disjoint.
        if dist == 0:
            raise ValueError("dist should not be zero in this case")
        elif dist == -1:
            dist = baseA - baseB
        return dist


def checkCommutativity(map1, map2):
    '''
    Test the composite maps of map1 and map2 to determine if they both map to
    the same point for any point p.

    Returns the maximum distance of seperation between the two composite
    functions.
    '''
    if not isinstance(map1, Mapping):
        raise TypeError("Argument 1 must be of type 'Mapping'")
    if not isinstance(map2, Mapping):
        raise TypeError("Argument 2 must be of type 'Mapping'")
    # generate the composite functions
    fog = lambda p: map1(map2(p))
    gof = lambda p: map2(map1(p))
    # generate list of test points
    testpoints = []
    divisions = int(N**2/M)
    increment = N / divisions
    for arm in xrange(T):
        for n in xrange(divisions+1):
            testpoints.append(Point(arm, increment*n))
    # keep track of max seperation
    dist = -1
    for p in testpoints:
        if map1(p) is None:
            raise ValueError("map1 is not complete.")
        if map2(p) is None:
            raise ValueError("map2 is not complete.")
        d = (fog(p) - gof(p))
        if d > dist or dist == -1:
            dist = d
    return dist
