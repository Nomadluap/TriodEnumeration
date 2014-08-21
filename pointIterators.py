'''
pointIterators.py - Functions for iterating over Vertices and Points. 
'''
from abc import ABCMeta
from config import N, M, T
from mapping import Point, Vertex


class VertexIterator(object):
    '''
    An abstract base class for DomainVertexIterator and CodomainVertexIterator.
    '''
    __metaclass__ = ABCMeta
    tmax = -1

    def __init__(self):
        self.arm = 0
        self.t = -1

    def __iter__(self):
        return self

    def next(self):
        self.t += 1
        if self.t > self.tmax:
            self.t = 1
            self.arm += 1
        if self.arm >= T:
            raise StopIteration
        return Vertex(self.arm, self.t)


class DomainVertexIterator(VertexIterator):
    '''
    An iterator to iterate over points in the domain.
    '''
    tmax = N


class CodomainVertexIterator(VertexIterator):
    '''
    An iterator to iterate over points in the codomain
    '''
    tmax = M
