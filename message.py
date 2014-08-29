'''
message.py - Classes representing messages sent over the MPI connection
'''
from abc import ABCMeta
from mapping import Mapping, MappingPair


class Message(object):
    '''
    Top-level message class. Abstract.
    '''
    __metaclass__ = ABCMeta

    sourceRank = None

    def __init__(self):
        pass


class DonePairMesage(Message):
    '''
    Message from worker indicating that it is done working on a pair and is
    requesting a new one.

    Pair metrics are returned with the message.
    '''
    countTotal = 0
    countFailures = 0

    def __init__(self, rank, total, failures):
        self.sourceRank = rank
        self.countTotal = total
        self.countFailures = failures


class StatusMessage(Message):
    '''
    Message from a worker reporting partial status.
    '''
    countTotal = 0
    countFailures = 0

    def __init__(self, rank, total, failures):
        self.sourceRank = rank
        self.countTotal = total
        self.countFailures = failures


class NewPairMessage(Message):
    '''
    Message from the master process to a worker containing a new pair of
    partial functions to operate on.
    '''
    pair = None

    def __init__(self, pair):
        if not isinstance(pair, MappingPair):
            raise TypeError("Argument must be of type 'MappingPair'")
        self.pair = pair


class StopMessage(Message):
    '''
    Message from the master process to a worker to stop all operation and exit.
    '''
    def __init__(self):
        pass


class ReportPairMessage(Message):
    '''
    Message from worker to master to log properties of the following function
    pair.
    '''
    disjointnessNumber = -1
    commutativityNumber = -1
    pair = None

    def __init__(self, rank, pair, dNumber, cNumber):
        self.sourceRank = rank
        self.pair = pair
        self.disjointnessNumber = dNumber
        self.commutativityNumber = cNumber

