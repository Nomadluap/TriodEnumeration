'''
mappingIterators.py - classes which facilitate iterating over different types of
mappings.

There are two distinct types of mapping iterators in this file: empty mapping
iterators and full mapping iterators.

Empty mapping iterators are intended for the overseer thread and are generally
in charge of generating pairs of empty maps which will eventually get sent to
worker threads.

Full mapping iterators are intended to be utilized inside worker threads in
order to complete the empty mappings given to them by the overseer thread. 
'''
from config import N, M, T
from mapping import Mapping, Vertex
from abc import ABCMeta, abstractmethod
from pointIterators import CodomainVertexIterator, DomainVertexIterator
from itertools import permutations, combinations


class MappingIterator(object):
    '''
    Abstract base class for empty and full mapping iterators.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def next(self):
        pass
    
    def __iter__(self):
        return self


class EmptyMappingIterator(MappingIterator):
    '''
    Abstract base class for empty mapping iterators.
    '''
    __metaclass__ = ABCMeta


class FullMappingIterator(MappingIterator):
    '''
    A mapping iterator which returns mappings based on an existing mapping.
    This iterator simply returns its constructor mapping.
    '''
    __metaclass__ = ABCMeta


class BasicEmptyMapIterator(EmptyMappingIterator):
    '''
    An empty mapping iterator which returns a mapping for each point in the
    codomain. Each mapping returned contains only this point as the basepoint.

    The optional skip argument specifies the number of mappings to skip before
    returning the first one to the calling function.
    '''
    def __init__(self, skip=0):
        self.iterator = CodomainVertexIterator()
        self.currentID = skip
        #skip the required number of mappings
        try:
            for i in range(skip):
                self.next()
        except StopIteration:
            pass

    def next(self):
        #throws StopIteration by itself when it's done.
        mapp = Mapping(basepoint=self.iterator.next())
        self.currentID += 1
        mapp.id = self.currentID
        return mapp


class EndpointEmptyMappingIterator(EmptyMappingIterator):
    '''
    An empty mapping iterator which takes every empty mapping created by
    BasicEmptyMapIterator and returns completions which have a valid
    endpointmap appended. 

    The optional skip argument specifies the number of mappings to skip before
    returning the first one to the calling function.
    '''
    def __init__(self, skip=0):
        self.id = skip
        self.domainPoints = list(DomainVertexIterator())

        self.mapIterator = BasicEmptyMapIterator()
        self.epmIterator = permutations(self.domainPoints, T)

        self.currentMap = None
        self.currentEpm = None
        # advance the iterator
        for i in range(skip):
            self.next()

    def next(self):
        while True:
            try:  # try to advance the epm iterator
                self.currentEpm = self.epmIterator.next()
            except StopIteration:  # if we're at the end, advance the mapping
                # once we advance past the last mapping, the iteration is done
                # and mapiterator.next will throw a StopIteration.
                self.currentMap = self.mapIterator.next()
                # and reset the epmIterator
                self.epmIterator = permutations(self.domainPoints, T)
                self.currentEpm = self.epmIterator.next()
            # Now we have both a mapping and an epm. We can now perform a
            # sanity check to make sure the epm is valid.
            try:
                # test for distance
                for p1, p2 in combinations(self.currentEpm, 2):
                    if p2 - p1 < 2*M:
                        raise ValueError
                # test for tricky zero-values
                for arm in range(T):
                    if self.currentEpm[arm] == Vertex(0, 0) and \
                            self.currentMap(0, 0) != Vertex(arm, M):
                                raise ValueError
                # verify that dist(image of basepoint, endpoint) <=
                # dist(Vertex(0, 0), preimage of endpoint
                for arm in range(T):
                    if (self.currentMap(0, 0) - Vertex(arm, M)) > \
                       (Vertex(0, 0) - self.currentEpm[arm]):
                            raise ValueError
            except ValueError:
                continue
            else:
                break
        # at this point we have a valid epm and a mapping. Return the mapping.
        newmap = Mapping(self.currentMap)
        newmap.endpointMap = list(self.currentEpm)
        newmap.id = self.id
        return newmap


if __name__ == "__main__":
    for p in BasicEmptyMapIterator():
        print p



