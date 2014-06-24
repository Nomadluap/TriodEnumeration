#!/usr/bin/env python
from __future__ import division
from generators import completions
from comparitors import checkPartialDisjointness, checkCommutativity
from comparitors import checkSurjectivity
from overseer_mpi import CHECK_SURJECTIVITY, N, M, T
from mpiGlobals import *
from mpi4py import MPI


def main():
    #at this point, we have just been spawned. We need go get the comm object
    comm = MPI.Comm.Get_parent()
    rank = comm.Get_rank()
    print "I am worker process {}".format(rank)
    #now we loop and await a command
    command = comm.recv(tag=TAG_WORKER_COMMAND)
    while command != COMMAND_STOP:
        #if command is not COMMAND_STOP, then we assume that it's a pair to
        #operate on. Therefore, operate on it.
        dummyWorker(command, comm)
        #report to the main thread that we are done and would like a new pair
        comm.send((REPORT_DONEPAIR, rank), tag=TAG_WORKER_REPORT)
        #and get the next command
        command = comm.recv(tag=TAG_WORKER_COMMAND)
    #we got a stop,now wait and quit
    #if we are rank zero, then we have to signal the reader thread to quit
    comm.Barrier()
    MPI.Finalize()


def pairWorker(pair, comm):
    '''
    Checks a pair of empty maps for disjointness and commutativity.

    @param pair the pair to operate on
    @param comm the intercomminication object to the master process.
    '''

    #now we have a pair of empty maps. At this point we should generate
    #completions for each and test them against eachother.
    #to speed up execution a bit, a disjointness check will be completed
    #about halfway through generation, so that we do not waste resources
    #on maps that fail early.

    #we needed to pack the queue object with the pair to work with Pool.map()
    print "starting pair: {}".format(pair)
    empty1, empty2 = pair
    for partial1 in completions(empty1, N, M, T, length=N//2):
        for partial2 in completions(empty2, N, M, T, length=N//2):
            #check partial disjointness, only proceed if true
            if checkPartialDisjointness(partial1, partial2, N, M, T) is False:
                continue
            #if we pass the partial disjointness check at this point, then
            #we may continue with this part of the generation
            for map1 in completions(partial1, N, M, T):
                #optionally skip a mapping if it is not surjective
                if CHECK_SURJECTIVITY and not checkSurjectivity(map1, N, M, T):
                    continue
                for map2 in completions(partial2, N, M, T):
                    if CHECK_SURJECTIVITY and not checkSurjectivity(
                            map2, N, M, T):
                        continue
                    #now we should have two complete maps. We can now check
                    #for both disjointness and commutivity
                    #checkDisjointness is the faster function, so do it
                    #first
                    if checkPartialDisjointness(map1, map2, N, M, T) is True:
                        #debug bypass the commutivity checker---------------V
                        if checkCommutativity(map1, map2, N, M, T) is True:
                            #now we have found a pair which passes the test.
                            #append it to the good list.
                            reportSuccess((map1, map2), comm)


def reportSuccess(pair, comm):
    '''
    report a success back to the master-process.
    @param pair the pair to report
    @param comm
    the comm channel to send the message to
    '''
    comm.send((REPORT_FOUNDPAIR, pair), tag=TAG_WORKER_REPORT)


def dummyWorker(pair, comm):
    '''
    A dummy worker used for testing to ensure that the messages get passed
    corretcly where they need to go

    '''
    reportSuccess(pair, comm)

if __name__ == "__main__":
    main()
