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
from threading import Thread
from datetime import datetime
from mpi4py import MPI
from mpiGlobals import *

#globals. These are important

N = 5
M = 3
T = 3
#filename to save results to
FILENAME = 'mapping_results.txt'

#number of mapping worker-processes
NUM_WORKERS = 4
#whether to discard mappings which are not surjective
CHECK_SURJECTIVITY = True
#name of the worker process to execute
WORKER_EXEC = 'overseer-mpi-worker.py'


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
    comm = MPI.COMM_SELF.Spawn(WORKER_EXEC, maxprocs=NUM_WORKERS)
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

    #readerThread logs the results of the calculations
    readerThread = Thread(target=result_reader, args=(comm,))
    readerThread.start()

    #now make a list of what each process is doing.
    #a value of True means that the process is currently doing work.
    #a value of False means that it has been stopped.
    status = [True for i in range(num_workers)]
    #Now we need to send an initial pair to each worker.
    for i in range(num_workers):
        pair = empty_pairs.next()
        comm.send(pair, dest=i, tag=TAG_WORKER_COMMAND)
    #now we need to wait for one of the processes to report that it is
    #done with a pair. Then, go through and keep on sending new pairs
    for pair in empty_pairs:
        #wait for a process to report that it is done with a pair
        #it will then send its worker rank back
        worker_rank = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_DONE_PAIR)
        #and send that worker a new pair
        comm.send(pair, dest=worker_rank, tag=TAG_WORKER_COMMAND)
    #at this point, we have exhausted all pairs. Now, when a process reports
    #that it is done, we send it the 'stop' command.
    #worker process 0 is special: it will send the 'stop' command to the
    #reader thread.
    while True not in status:
        worker_rank = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_DONE_PAIR)
        status[worker_rank] = False
        #don't send to rank 0 until they have all stopped
        if worker_rank != 0:
            comm.send(COMMAND_STOP, dest=worker_rank, tag=TAG_WORKER_COMMAND)
    #now all processes have stopped, send the stop command to worker 0
    comm.send(COMMAND_STOP, dest=0, tag=TAG_WORKER_COMMAND)
    #worker 0 will tell the thread to stop, now we must join it
    readerThread.join()
    #and now we should be done.
    MPI.Finalize()


def result_reader(comm):
    '''
    Listens for results from the worker processes and logs the results to a
    file.
    @param comm the intercommunicator to the worker processes
    '''
    f = open(FILENAME, 'a')
    #header
    f.write("new test:: started: {}\n".format(str(datetime.now())))
    f.flush()

    result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_REPORT_SUCCESS)
    while result != COMMAND_STOP:
        print "FOUND ONE:"
        print "\tmap 1: {} \n\tmap 2: {}".format(*result)
        f.write("FOUND ONE:\n")
        f.write("\tmap 1: {} \n\tmap 2: {}".format(*result))
        f.flush()
        result = comm.recv(source=MPI.ANY_SOURCE, tag=TAG_REPORT_SUCCESS)
    #footer
    print 'finished checking :: time: {}'.format(str(datetime.now()))
    f.write("finished checking :: time: {}\n".format(str(datetime.now())))
    f.close()
    return

if __name__ == "__main__":
    main()
#TODO: don't make so many new variables.
