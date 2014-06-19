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
from generators import completions
from comparitors import checkPartialDisjointness, checkCommutativity, checkSurjectivity
from multiprocessing import Pool, Manager
from threading import Thread
from datetime import datetime

#globals. These are important

N = 5
M = 3
T = 3
#filename to save results to
FILENAME='mapping_results.txt'
#maximum size of queue to report results to
QUEUE_SIZE = 10000
#number of mapping worker-processes
NUM_THREADS = 3
#whether to discard mappings which are not surjective
CHECK_SURJECTIVITY=True

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
    man = Manager()
    pairQueue = man.Queue(QUEUE_SIZE) # holds pairs which pass

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
    
    
    #readerThread logs the results of the calculations
    readerThread = Thread(target=result_reader, args=(pairQueue,))
    readerThread.start()
    
    #since we only have a small number of cores, we probably 
    #want to spawn a thread for every pair here.
    pool = Pool(processes=NUM_THREADS)
    #we need to pack q in with the iterable since that's how map works.
    pool.map(pairWorker, iterable=( (pairQueue,pair) for pair in empty_pairs))
    #now wait on the queue for things to be passed back
    #once the pool has finished its work, send a sentinel value
    #into the queue to tell the writer thread to stop what it's doing
    pairQueue.put("DONE")
    
    #now join the readerThread
    readerThread.join()
    #and now we should be done.



        

def result_reader(q):
    '''
    Grabs the results of the pairWorker pool and writes results to both a file
    and to stdout. 
    @param q the queue to read results from
    @param f the file to write to
    '''
    f = open(FILENAME, 'a')
    f.write("new test:: started: {}\n".format( str(datetime.now()) ))
    f.flush()
    result = q.get()
    while result != "DONE":
        print "FOUND ONE:"
        print "\tmap 1: {} \n\tmap 2: {}".format(*result)
        f.write("FOUND ONE:\n")
        f.write("\tmap 1: {} \n\tmap 2: {}\n".format(*result))
        f.flush()
        result = q.get()
    print 'finished checking :: time: {}'.format(str(datetime.now()))
    f.write("finished checking :: time: {}\n".format(str(datetime.now())))
    f.close()
    return

    
def pairWorker(q_and_pair):

    #now we have a pair of empty maps. At this point we should generate
    #completions for each and test them against eachother.
    #to speed up execution a bit, a disjointness check will be completed
    #about halfway through generation, so that we do not waste resources 
    #on maps that fail early.
    
    #we needed to pack the queue object with the pair to work with Pool.map() 
    q, pair = q_and_pair
    print "Starting pair: {}".format(pair)
    empty1, empty2 = pair
    for partial1 in completions(empty1, N, M, T, length=N//2):
        for partial2 in completions(empty2, N, M, T, length=N//2):
            #check partial disjointness, only proceed if true
            if checkPartialDisjointness(partial1, partial2, N, M, T)==False:
                continue
            #if we pass the partial disjointness check at this point, then
            #we may continue with this part of the generation
            for map1 in completions(partial1, N, M, T):
                #optionally skip a mapping if it is not surjective
                if CHECK_SURJECTIVITY and not checkSurjectivity(map1, N, M, T):
                    continue
                for map2 in completions(partial2, N, M, T):
                    if CHECK_SURJECTIVITY and not checkSurjectivity(map2, N, M, T):
                        continue
                    #now we should have two complete maps. We can now check
                    #for both disjointness and commutivity
                    #checkDisjointness is the faster function, so do it 
                    #first
                    if checkPartialDisjointness(map1, map2, N, M, T)==True:
                        #debug bypass the commutivity checker---------------V
                        if checkCommutativity(map1, map2, N, M, T)==True:
                            #now we have found a pair which passes the test.
                            #append it to the good list.
                            q.put((map1, map2))

    #now we're done.
                        
                    
                
        

if __name__ == "__main__":
    main()
    
    
    
    
#TODO: don't make so many new variables. 
    
