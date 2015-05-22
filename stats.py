#!/usr/bin/python2
'''
Generate stat values for different mapping generations. 
'''
from config import N, M, T
from mapping import Mapping
from pointIterators import CodomainVertexIterator
from itertools import permutations, combinations
from mappingIterators import *
from multiprocessing import Pool
from comparitors import checkDisjointness   

grandtotal = 0

def countCompletions(bpPair):
    bp1, bp2 = bpPair
    count = 0
    #count every successful mapping
    for i in SurjectiveMappingIterator(bp1):
        for j in SurjectiveMappingIterator(bp2):
            count += 1
    #and return 
    return count

if __name__ == "__main__":
    basepoints = list(EndpointEmptyMappingIterator())
    bpPairs = list(permutations(basepoints, 2))
    raw_input("Press any key to begin")
    #p = Pool(processes=4)
    f = open("results-stats.txt", "a")
    f.write("starting new run\n\n\n")
    for i in xrange(len(bpPairs)):
        print "starting pair: {} of {}: {}".format(i, len(bpPairs), bpPairs[i])
        f.write("starting pair: {} of {}: {}\n".format(i, len(bpPairs),
            bpPairs[i]))
        grandtotal += countCompletions(bpPairs[i])
        print "grand total so far: {}".format(grandtotal)
        f.write("grand total so far: {}\n".format(grandtotal))
        f.flush()

    print "super grand total: {}".format(grandtotal)
    f.write("super grand total: {}".format(grandtotal))
    f.close()

        


    #results = p.map(countCompletions, bpPairs)

    raw_input("press any key")
