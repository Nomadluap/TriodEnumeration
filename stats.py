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


def countCompletions(basemap):
    total = 0
    surjective = 0
    #count every successful mapping
    for i in FullMappingIterator(basemap):
        total += 1
        if checkSurjectivity(i):
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
    basemaps = list(BasicEmptyMapIterator())
    raw_input("Press any key to begin")
    #p = Pool(processes=4)
    f = open("results-stats.txt", "a")
    f.write("starting new run\n\n\n")
    f.write("N= {} M={} T={}\n".format(N, M, T))
    for i in xrange(len(basemaps)):
        print "starting basemap: {} of {}: {}".format(i, len(basemaps), basemaps[i])
        f.write("starting basemap: {} of {}: {}\n".format(i, len(basemaps),
            basemaps[i]))

        total, surjective= countCompletions(basemaps[i])
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
