#!/usr/bin/env python
'''
The overseer module is the module that actually handles the generation of the
functions, and orchestrates all the other functions. In the future, this
module will be the one that dispatches threads or worker nodes in a cluster
environment.


"--mca mpi_yield_when_idle 1" to stop busy-waiting of threads.

Created on Jun 9, 2014

@author: paul
'''
from __future__ import division
from T_od import Point
from itertools import combinations, permutations
from datetime import datetime
from mpi4py import MPI
from mpiGlobals import *
import generators
from comparitors import checkPartialDisjointness
import sys


#---GLOBAL VARIABLES---
N = 6
M = 2
T = 3
#filename to write results to
FILENAME = 'mapping_results.txt'
#check for surjectivity of maps before checking commutativity
CHECK_SURJECTIVITY = True
#function the worker uses to generate completions
#either generators.completions_surjective or generators.completions
GENERATOR_FUNC = generators.completions_surjective
#how often workers report status updates back to the main process
STATUS_UPDATE_INTERVAL = 1000000
#amount to complete each map before sending to workers.
PREWORKER_COMPLETION_LENGTH = 0
#Generate empty mappings with endpoint maps pre-defined
PREWORKER_GENERATE_ENDPOINT_MAPS = True
#---END GLOBAL VARIABLES---

#file object used by the logger
f = None

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


def generate_pairs(basepoints):
    '''
    generate the list of pairs to send to the workers.
    '''
    log("Beginning generation of pairs...")
    #first generate some empty mappings
    empty_mappings = []
    for bp in basepoints:
        thisMap = [bp]
        for i in xrange(T):
            thisMap.append(tuple())
        empty_mappings.append(thisMap)
    #now we need to pre-complete each map to the specified length.
    #and return every possible combination of these partial mappings.
    if PREWORKER_GENERATE_ENDPOINT_MAPS:
        epm_mappings = []
        for mapping in empty_mappings:
            points = [Point(0, 0)]
            for arm in range(0, T):
                for t in range(1, N+1):
                    points.append(Point(arm, t))
            #take every three-permutation of points
            for epm in permutations(points, 3):
                #if we're trying to map the basepoint to and endpoint and it isn't
                #already there, then skip this permutation
                #also enforce proper seperation of endpoint terms.
                try:
                    #test for proper distances
                    for p1, p2 in combinations(epm, 2):
                        if p2 - p1 < 2*M:
                            raise ValueError
                    #check for tricky zero-values
                    for arm in range(3):
                        if epm[arm] == Point(0, 0) and \
                           mapping[0] != Point(arm, M):
                            raise ValueError
                    #verify that dist(image of basepoint, endpoint)
                    #<= dist(Point(0, 0), preimage of endpoint)
                    for arm in range(3):
                        if (mapping[0] - Point(arm, M)) >\
                           (Point(0, 0) - epm[arm]):
                            raise ValueError
                    #set the epm
                    mapping_new = list(mapping)
                    mapping_new[0] = Point(mapping_new[0])
                    mapping_new[0].epm = list(epm)

                    epm_mappings.append(mapping_new)
                except ValueError:
                    continue
        log("Ending genreeation of pairs...")
        return combinations(epm_mappings, 2)

    elif PREWORKER_COMPLETION_LENGTH == 0:
        log("Ending genreeation of pairs...")
        return combinations(empty_mappings, 2)
    
    #else do a partial generation
    #generate every completion
    else:
        partialMaps = []
        for emptyMap in empty_mappings:
            for partial in generators.completions(emptyMap, N, M, T,
                                                  length=PREWORKER_COMPLETION_LENGTH):
                partialMaps.append(partial)
        #now every combination. Throw away any pair which shares the same basepoint
        partialPairs = []
        for pair in combinations(partialMaps, 2):
            m1, m2 = pair
            if not checkPartialDisjointness(m1, m2, N, M, T):
                continue
            else:
                partialPairs.append(pair)
        log("Ending genreeation of pairs...")
        return partialPairs.__iter__()


def main_master(comm):
    global f
    #Open file for writing
    f = open(FILENAME, 'a')
    #spawn worker processes and establish an intracommunicator
    num_workers = comm.Get_size()

    basepoints = generate_basepoints()
    empty_pairs = generate_pairs(basepoints)
    #header
    log("new test:: started: {}".format(str(datetime.now())))
    log("N = {}, M = {}, T = {}".format(N, M, T))
    log("CHECK_SURJECTIVITY: {}, GENERATOR_FUNC: {}".format(
        CHECK_SURJECTIVITY, str(GENERATOR_FUNC).split()[1]))
    log("PREWORKER_COMPLETION_LENGTH: {}".format(PREWORKER_COMPLETION_LENGTH))
    log("PREWORKER_GENERATE_ENDPOINT_MAPS: {}".format(
        PREWORKER_GENERATE_ENDPOINT_MAPS))
    log("-----")
    comm.Barrier()
    #wait for all workers to print initilization
    comm.Barrier()

    #now make a list of what each process is doing.
    #a value of True means that the process is currently doing work.
    #a value of False means that it has been stopped.
    status = [True for i in range(num_workers)]
    status[0] = False
    #Now we need to send an initial pair to each worker.
    for i in range(1, num_workers):
        try:
            pair = empty_pairs.next()
            log("Worker # {} starting pair: {}".format(i, pair))
            log("\twith endpointMaps: {} | {}".format(
                pair[0][0].epm, pair[1][0].epm))
            comm.send(pair, dest=i, tag=TAG_WORKER_COMMAND)
        except StopIteration:
            break
    #now we need to wait for one of the processes to report that it is

    while True in status:
        kind, result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_WORKER_REPORT)
        #if we found a pair, send a new pair
        if kind == REPORT_DONEPAIR:
            try:
                #send a new pair if one is available
                newpair = empty_pairs.next()
                log("Worker # {} starting pair: {}".format(result, newpair))
                log("\t with endpointMaps: {} | {}".format(
                    newpair[0][0].epm, newpair[1][0].epm))
                comm.send(newpair, dest=result, tag=TAG_WORKER_COMMAND)
            except StopIteration:
                #if we have no pairs left to test, tell the process to stop
                status[result] = False
                comm.send(COMMAND_STOP, dest=result, tag=TAG_WORKER_COMMAND)
        #log any reports of success
        elif kind == REPORT_FOUNDPAIR:
            result_writer(result, f)
        elif kind == REPORT_STATUS:
            #unpack and print a pretty message
            workerRank, counts = result
            log("Worker # {} status: {}".format(workerRank, counts))

    #and finish the file.
    log("finished checking :: time: {}".format(str(datetime.now())))
    f.close()

    #and now we should be done.
    comm.Barrier()
    MPI.Finalize()


def result_writer(result, f):
    '''
    commits a pair to the log
    '''

    log("FOUND ONE:")
    log("\tmap 1: {} \n\tmap 2: {}".format(*result))


def log(string):
    '''
    logs the string to both the console and the file
    '''
    global f
    print string
    f.write(string + "\n")
    f.flush()

if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        main_master(comm)
    else:
        from overseer_worker import main_worker
        main_worker(comm)
#TODO: don't make so many new variables.
