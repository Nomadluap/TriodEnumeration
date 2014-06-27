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
from itertools import combinations
from datetime import datetime
from mpi4py import MPI
from mpiGlobals import *

#globals. These are important

N = 3
M = 2
T = 3
FILENAME = 'mapping_results.txt'
NUM_WORKERS = 3
CHECK_SURJECTIVITY = True
WORKER_EXEC = 'python'
WORKER_ARGV = ['overseer_mpi_worker.py']
STATUS_UPDATE_INTERVAL = 1000000


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
    #spawn worker processes and establish an intercommunicator
    print "About to try to spawn {} workers.".format(NUM_WORKERS)
    comm = MPI.COMM_SELF.Spawn(WORKER_EXEC, args=WORKER_ARGV,
                               maxprocs=NUM_WORKERS)
    num_workers = comm.Get_remote_size()

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

    #Open file for writing
    f = open(FILENAME, 'a')
    #header
    f.write("new test:: started: {}\n".format(str(datetime.now())))
    print "new test:: started: {}\n".format(str(datetime.now()))
    f.flush()

    #now make a list of what each process is doing.
    #a value of True means that the process is currently doing work.
    #a value of False means that it has been stopped.
    status = [True for i in range(num_workers)]
    #Now we need to send an initial pair to each worker.
    for i in range(num_workers):
        pair = empty_pairs.next()
        print "Worker # {} starting pair: {}".format(i, pair)
        f.write("Worker # {} starting pair: {}".format(i, pair))
        f.flush()
        comm.send(pair, dest=i, tag=TAG_WORKER_COMMAND)
    #now we need to wait for one of the processes to report that it is

    while True in status:
        kind, result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_WORKER_REPORT)
        #if we found a pair, send a new pair
        if kind == REPORT_DONEPAIR:
            try:
                #send a new pair if one is available
                newpair = empty_pairs.next()
                print "Worker # {} starting pair: {}".format(result, newpair)
                f.write("Worker # {} starting pair: {}".format(result, newpair))
                f.flush()
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
            print "Worker # {} status: {}".format(workerRank, counts)
            f.write("Worker # {} status: {}\n".format(workerRank, counts))
            f.flush()

    #and finish the file.
    print 'finished checking :: time: {}'.format(str(datetime.now()))
    f.write("finished checking :: time: {}\n\n".format(str(datetime.now())))
    f.close()

    #and now we should be done.
    comm.Barrier()
    MPI.Finalize()


def result_writer(result, f):
    '''
    commits a pair to the log
    '''

    print "FOUND ONE:"
    print "\tmap 1: {} \n\tmap 2: {}".format(*result)
    f.write("FOUND ONE:\n")
    f.write("\tmap 1: {} \n\tmap 2: {}\n".format(*result))
    f.flush()

if __name__ == "__main__":
    main()
#TODO: don't make so many new variables.
