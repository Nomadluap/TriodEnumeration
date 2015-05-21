#!/usr/bin/python2
'''
Generate stat values for different mapping generations. 
'''
from config import N, M, T
from mapping import Mapping
from pointIterators import CodomainVertexIterator
from itertools import permutations, combinations
from mappingIterators import FullMappingIterator
from multiprocessing import Pool
from comparitors import checkDisjointness   


def countCompletions(bpPair):
    print "starting pair: {}".format(bpPair)
    bp1, bp2 = bpPair
    count = 0
    #mapping generators 
    first = FullMappingIterator(Mapping(bp1), length=2)
    second  = FullMappingIterator(Mapping(bp2), length=2)
    #count every successful mapping
    for i in first:
        for j in second:
            print i, j
            if checkDisjointness(i, j) == 0:
                continue
            for ii in FullMappingIterator(i):
                for jj in FullMappingIterator(j):
                    count += 1
    #and return 
    return count

if __name__ == "__main__":
    basepoints = list(CodomainVertexIterator())
    bpPairs = permutations(basepoints, 2)
    print "Pairs are: {}".format(bpPairs)
    raw_input("Press any key to begin")
    p = Pool(processes=4)

    results = map(countCompletions, bpPairs)
    print "Results are: {}".format(results)
    print "sum: {}".format(sum(results))
    raw_input("press any key")
