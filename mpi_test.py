#!/usr/bin/env python
from mpi4py import MPI
from mapping import Mapping, Vertex

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
    comm.send(m, dest=0)
    print "worker: done sending"


if __name__ == "__main__":
    if rank == 0:
        main_master()
    else:
        main_worker()
    MPI.Finalize()
