#!/usr/bin/env python
'''
Overseer.py - Module which oversees searching for pairs of triod mappings that
are both disjoint as well as commutative.

Changing of parameters is done in config.py.
'''
from __future__ import division
from mpi4py import MPI
from config import LOGFILE, N, M, T, PAIRSKIP, WORKER_REPORT_INTERVAL
from mappingIterators import SurjectiveMappingIterator
from mappingIterators import EndpointEmptyMappingPairIterator
from datetime import datetime
from comparitors import checkCommutativity, checkDisjointness
from message import StopMessage, NewPairMessage, ReportPairMessage
from message import StatusMessage, DonePairMesage, Message
from mapping import MappingPair, Mapping

# file object used by logger
f = None
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_workers = comm.Get_size()-1


def main_master():
    '''
    Main function for master process.
    Responsible for generating, sending pairs and collecting input.
    '''
    global f
    f = open(LOGFILE, 'a')

    counts = {'pairsSent': 0, 'pairsDone': 0, 'totalCompletions': 0,
              'completionsPassed': 0}
    # First, main_master prints startup information
    report("")
    report("---NEW TEST:: started: {}".format(str(datetime.now())))
    report("N = {}, M = {}, T = {}, PAIRSKIP:{}".format(N, M, T, PAIRSKIP))
    report("Workers: {}".format(num_workers))
    report("")
    # then wait for all workers to print their init.
    comm.Barrier()
    # workers working...
    comm.Barrier()
    # empty pair generator
    pairgen = EndpointEmptyMappingPairIterator()
    status = [True for i in range(num_workers+2)]
    status[0] = False
    # send initial pairs
    for i in range(1, num_workers+1):
        try:
            pair = pairgen.next()
            report_startpair(i, pair)
            comm.send(NewPairMessage(pair), dest=i)
            counts['pairsSent'] += 1
        # if we run out of pairs early, tell worker to stop
        except StopIteration:
            status[i] = False
            comm.send(StopMessage(), dest=i)

    # now wait for replies and act accordingly
    while True in status:
        # get reply
        reply = comm.recv(source=MPI.ANY_SOURCE)
        i = handle_reply(reply)
        # worker wanting more pairs
        if i is not None:
            counts['pairsDone'] += 1
            try:
                pair = pairgen.next()
                report_startpair(i, pair)
                comm.send(NewPairMessage(pair), dest=i)
                counts['pairsSent'] += 1
            # run out of pairs, tell worker to stop.
            except StopIteration:
                status[i] = False
                comm.send(StopMessage(), dest=i)
    # by now, all workers have stopped.
    report("---FINISHED:: time: {}".format(str(datetime.now())))
    report(counts)

    comm.Barrier()
    MPI.Finalize()


def main_worker():
    '''
    Main function for worker processes.
    Repsonsible for generating completions of pairs and sending reports back to
    master process.
    '''
    # wait for master to print initialization
    comm.Barrier()
    print "Worker #{:0>2d} init".format(rank)
    # pass back to master
    comm.Barrier()
    # main worker loop
    while True:
        # recieve a message from any worker
        message = comm.recv(source=0)
        if isinstance(message, StopMessage):
            break
        elif isinstance(message, NewPairMessage):
            # do the pair completion and then return.
            message = worker_processPair(message.pair)
            comm.send(message)
        else:
            raise TypeError("Got bad message: {}".format(message))
    # done, wait for master and quit
    comm.Barrier()
    MPI.Finalize()


def worker_processPair(pair):
    '''
    Actual processing of a pair by a worker goes here.

    Returns a DonePairMesage when complete  

    '''
    countTotal = 0
    countFailures = 0
    # unpack the pair
    map1 = pair[0]
    map2 = pair[1]
    #perform type-checking just in case
    if not (isinstance(map1, Mapping) and isinstance(map2, Mapping)):
        raise TypeError("map1 and map2 must be mapping objects")
    # start by completing half way and checking disjointness
    halfLength = N // 2
    for pm1 in SurjectiveMappingIterator(map1, length=halfLength):
        for pm2 in SurjectiveMappingIterator(map2, length=halfLength):
            #if mappings are not disjoint, try again
            if checkDisjointness(pm1, pm2) == 0:
                countTotal += 1
                countFailures += 1
                worker_periodicReport(countTotal, countFailures)
                continue
            #finish completion
            for m1 in SurjectiveMappingIterator(pm1):
                for m2 in SurjectiveMappingIterator(pm2):
                    djnum = checkDisjointness(m1, m2)
                    if djnum == 0:
                        countTotal += 1
                        countFailures += 1
                        worker_periodicReport(countTotal, countFailures)
                        continue
                    # if we pass disjointness, then report the pair
                    countTotal += 1
                    worker_periodicReport(countTotal, countFailures)
                    comnum = checkCommutativity(m1, m2)
                    report = ReportPairMessage(rank, MappingPair(m1, m2),
                                               djnum, comnum)
                    comm.send(report)
    # done pair. Return a DonePair message
    message = DonePairMesage(rank, countTotal, countFailures)
    return message


def worker_periodicReport(countTotal, countFail):
    if countTotal % WORKER_REPORT_INTERVAL == 0:
        report = StatusMessage(rank, countTotal, countFail)
        comm.send(report)


def report(s):
    '''
    Report the supplied string to both standard out and the log file.
    '''
    global f
    print s
    f.write(str(s) + '\n')
    f.flush()


def report_startpair(i, pair):
    '''
    report that worker i is starting pair 'pair'
    '''
    report("Worker #{:0>2d} starting pair:".format(i))
    report("\tPair id: {}".format(pair.idnum))
    report("\tMap 1: {}".format(pair[0]))
    report("\tMap 1 epm: {}".format(pair[0].endpointMap))
    report("\tMap 2: {}".format(pair[1]))
    report("\tMap 2 epm: {}".format(pair[1].endpointMap))
    report("")


def handle_reply(reply):
    '''
    Responsible for handling responses of the worker processes

    If a 'done pair' message is recieved, return the rank of the messaging
    process. Otherwise, return None.
    '''
    if not isinstance(reply, Message):
        raise TypeError("reply must be of type 'Message'")
    if isinstance(reply, StatusMessage):
        wrank = reply.sourceRank
        wtotal = reply.countTotal
        wfail = reply.countFailures
        report("STATUS: worker#{}: total:{} fail:{}".format(wrank, wtotal,
                                                            wfail))
    elif isinstance(reply, DonePairMesage):
        wrank = reply.sourceRank
        wtotal = reply.countTotal
        wfail = reply.countFailures
        report("DONEPAIR: worker#{}: total:{} fail:{}".format(wrank, wtotal,
                                                              wfail))
        return wrank
    elif isinstance(reply, ReportPairMessage):
        wrank = reply.sourceRank
        djnum = reply.disjointnessNumber
        comnum = reply.commutativityNumber
        wpair = reply.pair
        report("PAIR REPORT")
        report("\tmap1:{}".format(wpair[0]))
        report("\tmap2:{}".format(wpair[1]))
        report("\tdisjointness number:{}".format(djnum))
        report("\tcommutativity number:{}".format(comnum))

    else:
        return


if __name__ == '__main__':
    if rank == 0:
        main_master()
    else:
        main_worker()
