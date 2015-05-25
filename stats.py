#!/usr/bin/python2
'''
Generate stat values for different mapping generations. 
'''
from config import N, M, T
from mapping import Mapping
from pointIterators import CodomainVertexIterator, DomainVertexIterator
from itertools import permutations, combinations
from mappingIterators import *
from multiprocessing import Pool
from comparitors import checkDisjointness   


def countCompletions(bpPair):
    bp1, bp2 = bpPair
    total = 0
    surjective = 0
    #count every successful mapping
    for i in FullMappingIterator(bp1):
        for j in FullMappingIterator(bp2):
            total += 1
            if checkSurjectivity(m):
                surjective+=1
    #and return 
    return (total, surjective)

def checkSurjectivity(m):
    '''check surjectivity of a map.'''
    ends = [False for i in range(T)]
    for v in DomainVertexIterator():
        if m(v)[1] == M:
            ends[m(v)[0]] = True
    if False in ends:
        return False
    else:
        return True 


if __name__ == "__main__":
    grandtotal = 0
    grandtotal_surjective = 0
    basemaps = list(EmptyMappingIterator())
    bpPairs = list(combinations(basemaps, 2))
    raw_input("Press any key to begin")
    #p = Pool(processes=4)
    f = open("results-stats.txt", "a")
    f.write("starting new run\n\n\n")
    for i in xrange(len(bpPairs)):
        print "starting pair: {} of {}: {}".format(i, len(bpPairs), bpPairs[i])
        f.write("starting pair: {} of {}: {}\n".format(i, len(bpPairs),
            bpPairs[i]))

        total, surjective= countCompletions(bpPairs[i])
        grandtotal += total
        grandtotal_surjective += surjective

        print "grand total so far: {} surjective: {}".format(grandtotal,
                grandtotal_surjective)
        f.write("grand total so far: {} surjective: {}\n".format(grandtotal,
            grandtotal_surjective))
        f.flush()

    print "super grand total: {} grand surjective: {}".format(grandtotal,
            grandtotal_surjective)
    f.write("super grand total: {} grand surjective: {}\n".format(grandtotal,
        grandtotal_surjective))
    f.close()

        


    #results = p.map(countCompletions, bpPairs)

    raw_input("press any key")
