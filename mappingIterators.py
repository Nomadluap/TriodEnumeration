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
->EndpointEmptyMappingPairIterator

Empty mapping iterators take no starting mapping, and generally return
non-complete mappings that need to be further completed. 

Partial mapping iterators usually take a starting mapping, and generate full
completions. They are generally used in the worker processes.
'''
from config import N, M, T
from mapping import Mapping, Vertex, MappingPair
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
        mapp = Mapping(self.iterator.next())
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

        self.currentMap = self.mapIterator.next()

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
                # Endpoint map cannot contain what is already the basepoint
                for arm in range(T):
                    if self.currentEpm[arm] == self.currentMap(0, 0):
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
    N = 0

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


class SurjectiveMappingIterator(FullMappingIterator):
    '''
    A full mapping iterator which only returns surjective completions of a
    mapping which also satisfy the endpointMap which is assigned to the
    mapping.

    Mappings will be completed to the specified length, or completely if length
    is not specified.

    The mappings will be generated using a stack approach.

    The approach will be similar to FullMappingIterator, however, instead of
    the completions being generated based on simple ajacency, they will be
    generated via a distance-to-endpoint method as follows:

    For every leg:
        1. Fill in every vertex which is pre-defined in the original mapping.
        3. for every point remaining in the leg:
            - Check if there are points in the endpointlist which lie in the
              unmapped portion of this leg. If more than one exist, take the
              one with the shortest distance to the shortest distance to the
              branch point. If none exist, then the completion list for this
              point will be the list generated by ajacentCodomain.
            - let X be the distance between the current domain point and the
              point which is listed in the endpoint map. Let Y be the distance
              between the endpoint vertex and the current point:
            - if X < Y, then the original mapping cannot be made to be
              surjective, and StopIteration will be raised.
            - if X == Y, then the only valid completion for this point will be
              in a direction toward the endpoint
            - if X == Y+1, then two valid completions exist: to remain on the
              same vertex and to go toward the endpoint.
            - Otherwise, if X > Y + 1, then any ajacent codomain point is a
              valid completion.
        4. Generate mapping completions in a way that is the same as
        FullMappingIterator, however replace the normal completion list
        generation with the one described above.
    '''
    originalMapping = None
    legs = None
    completions = None
    isFirst = False
    failOnFirst = False
    N = 0

    def surjCompletions(self, l, p):
        '''
        Get the completion list for the current point using the method
        described above.
        '''
        # print '----'
        # print 'getting surjective completion list for position', l, p
        # first, generate an object representing the partial mapping so far
        mapList = [self.originalMapping(0, 0)] + self.legs
        mapp = Mapping(mapList)
        # print '--working with mapping', mapp, '--'

        lastVertex = mapp(Vertex(l, p))
        # print 'lastVertex is', lastVertex
        # find the lowest endpoint in the endpointlist which is not yet mapped
        endpointIndex = None
        for i in range(T):
            v = None
            try:
                v = self.originalMapping.endpointMap[i]
            except IndexError:
                print "something went wrong!!!!!"
                print "i is {}, epm is {}".format(i,
                        self.originalMapping.endpointMap)
                raise IndexError

            # leg must be correct
            if v[0] != l:
                continue
            # must be larger than current point
            if v[1] <= p:
                continue
            # must be smallest in series
            if endpointIndex is None or v[1] < \
                    self.originalMapping.endpointMap[endpointIndex][1]:
                endpointIndex = i
        # if no endpoint found, return completions in the usual way.
        if endpointIndex is None:
            # print 'found no endpoint'
            # print 'returning:', lastVertex.ajacentCodomain()
            return lastVertex.ajacentCodomain()
        # print 'found endpoint, number=', endpointIndex
        # generate X and Y
        X = Vertex(l, p) - self.originalMapping.endpointMap[endpointIndex]
        Y = mapp(Vertex(l, p)) - Vertex(endpointIndex, M)
        # print 'x, y are', X, Y
        # mapping has no valid completions
        if X < Y:
            # print 'no valid completions'
            raise StopIteration
        # we are one space away yet already at the endpoint. We can't move.
        elif X == 1 and Y == 0:
            # print 'one off, only valid completion is to stay'
            # print 'returning:', [lastVertex]
            return [lastVertex]
        # we are already here. We must stay.
        elif X == 0 and Y == 0:
            # print 'were here, stay'
            # print 'returning:', [lastVertex]
            return [lastVertex]
        # only valid completion is toward the endpoint
        elif X == Y:
            # print 'only valid completion toward endpoint'
            # print 'returning:', [lastVertex.toward(Vertex(endpointIndex, M))]
            return [lastVertex.toward(Vertex(endpointIndex, M))]
        # remain in place or go towards
        elif X == Y + 1:
            # print 'completions: remain in place or advance'
            # print 'returning:', [lastVertex,
            #                    lastVertex.toward(Vertex(endpointIndex, M))]
            return [lastVertex, lastVertex.toward(Vertex(endpointIndex, M))]
        #otherwise we can go anywhere
        else:
            # print 'go anywhere'
            # print 'return:', lastVertex.ajacentCodomain()
            return lastVertex.ajacentCodomain()

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
        # originalMapping should have an endpointmap
        if len(originalMapping.endpointMap) != T:
            raise ValueError("Original mapping must have endpoint map")
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
                self.legs[i].append(oLeg[j])
                # Also append to the completion stack, since it is the only
                # 'valid completion' for that location
                self.completions[i].append([oLeg[j]])

        # now pre-load the first completion.
        try:
            for l in range(T):
                for p in range(len(self.legs[l]), self.N):
                    #get the completions list
                    cpl = self.surjCompletions(l, p)
                    self.completions[l].append(cpl)
                    self.legs[l].append(cpl[0])
            # signal that next() has not run yet
        except StopIteration:
            self.failOnFirst = True
        self.isFirst = True

    def next(self):
        #special condition for first run of next()
        if self.isFirst:
            if self.failOnFirst is True:
                raise StopIteration
            self.isFirst = False
            mapList = [self.originalMapping(0, 0)] + self.legs
            newMap = Mapping(mapList)
            newMap.endpointMap = self.originalMapping.endpointMap
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
        # print 'mutating at', l, p
        # print 'original point', self.legs[l][p]
        # print 'possible completions are:', self.completions[l][p]
        # now we change that vertex to the next one in the completion list
        # first find where we are at the moment in the completion line
        i = 0
        while self.legs[l][p] != self.completions[l][p][i]:
            i += 1
        # now go one higher and substitute that in
        self.legs[l][p] = self.completions[l][p][i+1]
        # print 'mutated to', self.legs[l][p]
        # and finally re-load the completion past that point
        # remembering to take into consideration pre-completed portions of the
        # mapping. First, complete the leg we're currently on, then the rest.
        originalLeg = l
        l, p = self._vIncrement(l, p)
        while l == originalLeg:
            cpl = self.surjCompletions(l, p)
            self.completions[l][p] = cpl
            self.legs[l][p] = cpl[0]
            l, p = self._vIncrement(l, p)
        # now do the remaining legs
        for l in range(l, T):
            p = 0
            # increment p until original mapping stops being defined.
            while self.originalMapping(l, p+1) is not None:
                p += 1
            #now finish the leg
            while p < self.N:
                cpl = self.surjCompletions(l, p)
                self.completions[l][p] = cpl
                self.legs[l][p] = cpl[0]
                p += 1

        #and now we have the next full mapping, so we can return it.
        mapList = [self.originalMapping(0, 0)] + self.legs
        newMap = Mapping(mapList)
        newMap.endpointMap = self.originalMapping.endpointMap
        return newMap


class EndpointEmptyMappingPairIterator(object):
    '''
    Generates pairs of endpoint empty mapping iterators
    '''
    gen = None
    idnum = 0

    def __init__(self, skip=None):
        self.gen = combinations(EndpointEmptyMappingIterator(), 2)
        if skip is not None:
            for i in range(skip):
                self.next()

    def next(self):
        class PairBad(Exception):
            def __init__(self):
                pass

        self.idnum += 1
        # gen.next raises StopIteration for us.
        p = None
        pp = None
        while True:
            try:
                p = self.gen.next()
                # elements of p must have differing basepoints
                if p[0](0, 0) == p[1](0, 0):
                    raise PairBad
                # none of the elements of the epm can be similar
                for i in range(T):
                    if p[0].endpointMap[i] == p[1].endpointMap[i]:
                        raise PairBad
            except PairBad:
                continue
            else:
                pp = MappingPair(self.idnum, p[0], p[1])
                break
        return pp

if __name__ == "__main__":
    print 'start...'
    for pm in EndpointEmptyMappingIterator():
        print 'original mapping is', str(pm)
#        print 'with endpointmap', str(pm.endpointMap)
#        for m in SurjectiveMappingIterator(pm):
#            print 'got', m

