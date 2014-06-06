'''
Created on Jun 4, 2014

@author: paul
'''
from generators import functionize
from __future__ import division
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
    baseA = partialMap1[0]
    armsA = partialMap1[1:]
    baseB = partialMap2[0]
    armsB = partialMap2[1:]
    #check for common base, remember that the base poi
    if baseA == baseB or baseA[1] == baseB[1] == 0:
        return False
    curA = 0
    curB = 0
    prevA = 0
    prevB = 0
    #compare each pair of arms
    for tArm in zip(armsA, armsB):
        armA, armB = tArm
        #both arms start at the basepoint
        prevA = baseA
        prevB = baseB
        #now step through every mutually defined point
        for i in xrange(min(len(armA, armB))):
            curA = armA[i]
            curB = armB[i]
            #if we find an issue, return false at every case.
            if equals(curA, curB):
                return False
            elif equals(curA, prevB) and equals(curB, prevA):
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
            testpoints.append((arm, increment * n))
    
    epsilon = 1/(N*M*2)
    #now do the actual testing
    for p in testpoints:
        if abs(fog(p) - gof(p)) < epsilon:
            continue
        else:
            return False
    #if we haven't returned False, then all points are equal
    return True

def equals(pointA, pointB):
    '''
    Test whether two points in tuple form are equal
    @return True if equal, False otherwise.
    '''
    if pointA == pointB:
        return True
    #special case for common zero point
    elif pointA[1] == pointB[1] == 0:
        return True
    else:
        return False