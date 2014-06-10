'''
The overseer module is the module that actually handles the generation of the 
functions, and orchestrates all the other functions. In the future, this 
module will be the one that dispatches threads or worker nodes in a cluster 
environment. 

Created on Jun 9, 2014

@author: paul
'''
from __future__ import division
from T_od import Point
from itertools import combinations
#globals. These are important

N = 3
M = 2
T = 3







def generate_basepoints():
    """
    Generate a list of possible basepoints.
    
    In order to make this approach easier to thread in the future, we can 
    initially divide the sample space based on where the basepoint lies. 
    In this way we can reduce the problem into (3M+1 choose 2) - M problems,
    each of which may be solved individually. This is a good start.
    """
    basepoints = [Point(0, 0)]
    for arm in xrange(T):
        for t in range(1, M+1):
            basepoints.append(Point(arm, t))
    return basepoints


def main():
    basepoints = generate_basepoints()
    #now construct an empty mapping for each basepoint
    empty_mappings = []
    for bp in basepoints:
        thisMap = [bp]
        #add correct number of empty legs
        for i in xrange(T):
            thisMap.append(tuple())
        empty_mappings.append(tuple(thisMap))
    #now we have a list of empty maps
    #now we can pull every combination of these and start the comparison.
    #since two maps with the same basepoint are definitely going to fail the
    #test, we can use the simple itertools.combinations() to get this list
    empty_pairs = combinations(empty_mappings, 2)
    #at this point we'd probably want to split into threads or something
    #but a loop is fine too
    for pair in empty_pairs:
        pass

if __name__ == "__main__":
    main()
    
    
    
    
    
    