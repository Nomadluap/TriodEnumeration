#!/usr/bin/env python
from mpi4py import MPI
from mapping import Mapping, Vertex, MappingPair
from message import NewPairMessage

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


def main_master():
    print "I am the master"
    print "master: getting object"
    ob = comm.recv(source=1)
    print "got the object"
    print ob


def main_worker():
    print "I am the worker"
    print "worker: sending the object"
    m = Mapping(Vertex(0, 0))
    n = Mapping(Vertex(0, 1))
    pair = MappingPair(3, m, n)
    comm.send(pair, dest=0)
    print "worker: done sending"


if __name__ == "__main__":
    if rank == 0:
        main_master()
    else:
        main_worker()
    MPI.Finalize()
