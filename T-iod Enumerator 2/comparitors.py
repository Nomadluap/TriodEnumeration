'''
Created on Jun 4, 2014

@author: paul
'''
from __future__ import division
from generators import functionize
from T_od import Point
from itertools import chain
def checkPartialDisjointness(partialMap1, partialMap2, N, M, T=3):
    '''
    Compares two partial T-od maps to ensure that existing aprts are properly
    disjoint. The functions should be passed in list form.
    
    @param partialMap1 the first mapping to test
    @param partialMap2 the second mapping to test
    @param N the number of nodes per leg in the domain T-od
    @param M the number of nodes per leg in the codomain T-od
    @param T the number of legs
    
    @return True if the mappings are disjoint, False otherwise.
    '''
    baseA = Point(partialMap1[0])
    armsA = partialMap1[1:]
    baseB = Point(partialMap2[0])
    armsB = partialMap2[1:]
    #check for common base, remember that the base poi
    if baseA == baseB or baseA[1] == baseB[1] == 0:
        return False
    curA = Point(0, 0)
    curB = Point(0, 0)
    prevA = Point(0, 0)
    prevB = Point(0, 0)
    #compare each pair of arms
    for tArm in zip(armsA, armsB):
        armA, armB = tArm
        #both arms start at the basepoint
        prevA = baseA
        prevB = baseB
        #now step through every mutually defined point
        for i in xrange(min(len(armA), len(armB))):
            curA = Point(armA[i])
            curB = Point(armB[i])
            #if we find an issue, return false at every case.
            if curA == curB:
                return False
            elif curA==prevB and curB==prevA:
                return False
            else:
                prevA = curA
                prevB = curB
                continue
    #at this point, if we haven't returned, we've found nothing
    return True
        

def checkCommutativity(map1, map2, N, M, T=3):
    '''
    Test the composite maps of map1 and map2 to determine if they both map to 
    the same point for any point p
    
    @param map1 the first map to test
    @param map2 the second map to test
    @param N the number of points per leg of the domain T-od
    @param M the number of points per leg of the codomain T-od
    @param T the number of legs
    @return True iff (fog)(t) == (gof)(t) for all t, False otherwise.
    '''
    #make some functions
    f = functionize(map1, N, M, T)
    g = functionize(map2, N, M, T)
    #compose
    fog = lambda p: f(g(p))
    gof = lambda p: g(f(p))
    #generate both the list of test points and the epsilon value.
    #there will be N^2/M test points per arm. 
    testpoints = []
    divisions = int(N**2/M)
    increment = N/ divisions
    for arm in xrange(T):
        for n in xrange(divisions+1):
            testpoints.append(Point(arm, increment * n))
    
    epsilon = 1/(N*M*2)
    #now do the actual testing
    #TODO: change this to work properly with tuples.
    for p in testpoints:
        if abs(fog(p) - gof(p)) < epsilon:
            continue
        else:
            return False
    #if we haven't returned False, then all points are equal
    return True

def checkSurjectivity(mapping, N, M, T=3):
    '''
    Test a mapping for surjectivity
    
    @param mapping the mapping to test
    @param N the number of nodes per leg in the domain triod
    @param M the number of nodes per leg in the codomain triod
    @param T the number of legs
    
    @return True if the map is surjective, False otherwise.
    '''
    #If the mapping reaches all of the endpoints, then it is reasonable to
    #expect that it is surjective.
    #first, make a list of endpoints of the codomain triod
    endpoints = [(t, M) for t in range(T)]
    #flatten the mapping
    mapPoints = mapping[0] + list(chain(*mapping[1:]))
    #now index for each of the endpoints independently
    for endpoint in endpoints:
        try:
            mapPoints.index(endpoint)
        except ValueError:
            return False
    return True
