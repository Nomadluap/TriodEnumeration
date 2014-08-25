'''
mappingIterators.py - classes which facilitate iterating over different types
of mappings.

The class heirarchy is as follows:
->MappingIterator(Abstract)
    ->EmptyMappingIterator(Abstract)
        ->BasicEmptyMapIterator
        ->EndpointEmptyMappingIterator
    ->FullMappingIterator
        ->SurjectiveMappingIterator

Empty mapping iterators take no starting mapping, and generally return
non-complete mappings that need to be further completed. 

Partial mapping iterators usually take a starting mapping, and generate full
completions. They are generally used in the worker processes.
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
    id = 0
    domainPoints = list(DomainVertexIterator())
    mapIterator = None
    epmIterator = None

    currentMap = None
    currentEpm = None

    def __init__(self, skip=0):
        self.mapIterator = BasicEmptyMapIterator()
        self.epmIterator = permutations(self.domainPoints, T)

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
        self.id += 1
        newmap.id = self.id
        return newmap


class FullMappingIterator(MappingIterator):
    '''
    A mapping iterator which returns every valid completion of the starting
    mapping. Mappings will be completed to the specified length, or completely
    if length is not specified.

    The mappings will be generated using a stack approach.
    '''
    originalMapping = None
    legs = None
    completions = None
    isFirst = False

    def __init__(self, originalMapping, length=None):
        self.N = N
        # type checking
        if not isinstance(originalMapping, Mapping):
            raise TypeError("First argument must be of type 'Mapping'")
        #redefine local N if length is specified.
        if length is not None:
            if not isinstance(length, int):
                raise TypeError("length argument must be int")
            if length < 0 or length > N:
                raise ValueError("length must be in range [0, N]")
            self.N = length

        self.originalMapping = originalMapping
        self.legs = [[] for i in range(T)]
        self.completions = [[] for i in range(T)]
        # pre-fill arms and completions with what's already in the mapping.
        for i in range(T):
            oLeg = self.originalMapping.getLeg(i)
            for j in range(self.N):
                if oLeg[j] is None:
                    break
                # append to the completion stack
                self.legs[i].append(j)
                # Also append to the completion stack, since it is the only
                # 'valid completion' for that location
                self.completions[i].append([oLeg[j]])

        # now pre-load the first completion.
        for l in range(T):
            prevPoint = self.originalMapping(l, len(self.legs[l]))
            for p in range(len(self.legs[l]), self.N):
                #get the completions list
                cpl = prevPoint.ajacentCodomain()
                self.completions[l].append(cpl)
                self.legs[l].append(cpl[0])
                prevPoint = cpl[0]
        # signal that next() has not run yet
        self.isFirst = True

    def _vIncrement(self, l, p):
        '''
        Increment stack counters l and p
        '''
        p += 1
        if p >= self.N:
            p = 0
            l += 1
        return l, p

    def next(self):
        #special condition for first run of next()
        if self.isFirst:
            self.isFirst = False
            mapList = [self.originalMapping(0, 0)] + self.legs
            newMap = Mapping(mapList)
            return newMap

        # we always start off with the previous complete mapping
        # Thus, we first move backwards down the mapping, finding the first
        # vertex which is not already at its last possible completion.
        l = T-1
        p = self.N - 1
        while self.legs[l][p] == self.completions[l][p][-1]:
            #if we get all the way down to l=0, p=0, we're done
            if l == 0 and (p == 0 or self.originalMapping(l, p) is not None):
                raise StopIteration
            if p == 0 or self.originalMapping(l, p) is not None:
                p = self.N - 1
                l -= 1
            else:
                p -= 1
        # now we change that vertex to the next one in the completion list
        # first find where we are at the moment in the completion line
        i = 0
        while self.legs[l][p] != self.completions[l][p][i]:
            i += 1
        # now go one higher and substitute that in
        self.legs[l][p] = self.completions[l][p][i+1]
        # and finally re-load the completion past that point
        # remembering to take into consideration pre-completed portions of the
        # mapping. First, complete the leg we're currently on, then the rest.
        originalLeg = l
        prevPoint = self.legs[l][p]
        l, p = self._vIncrement(l, p)
        while l == originalLeg:
            cpl = prevPoint.ajacentCodomain()
            self.completions[l][p] = cpl
            self.legs[l][p] = cpl[0]
            prevPoint = self.legs[l][p]
            l, p = self._vIncrement(l, p)
        # now do the remaining legs
        for l in range(l, T):
            p = 0
            # increment p until original mapping stops being defined.
            while self.originalMapping(l, p) is not None:
                p += 1
            # now get what the first completion should be from the completion
            # map of the last point in the original mapping
            prevPoint = self.originalMapping(l, p-1)
            cpl = prevPoint.ajacentCodomain()
            self.completions[l][p-1] = cpl
            self.legs[l][p-1] = cpl[0]
            p += 1
            #now finish the leg
            while p <= self.N:
                prevPoint = self.legs[l][p-2]
                cpl = prevPoint.ajacentCodomain()
                self.completions[l][p-1] = cpl
                self.legs[l][p-1] = cpl[0]
                p += 1

        #and now we have the next full mapping, so we can return it.
        mapList = [self.originalMapping(0, 0)] + self.legs
        newMap = Mapping(mapList)
        return newMap

if __name__ == "__main__":
    print 'start...'
    mapp = Mapping(Vertex(0, 0))
    print 'original map', mapp
    for m in FullMappingIterator(mapp, length=1):
        print m
