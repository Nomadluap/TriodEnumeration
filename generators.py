'''
Created on Jun 3, 2014

Functions for triod enumeration which generate things, including funciton
and mapping generators.

@author: paul
'''
from T_od import Point, Vertex
from itertools import permutations, combinations

DEBUG_PRINT = False


def completions(partialMap, N, M, T=3, mappingEnd=None, length=None):
    '''
    Generate a series of mappings which are completions of the partial mapping
    mapping_start.

    Generation will continue until the mapping generated is equivalent to
    mapping_end, or until all completions are exhausted if mapping_end is None.
    @param mapping_start the partially-complete mapping to iterate over
    @param N the number of nodes per leg in the domain T-od
    @param M the number of nodes per leg in the codomain T-od
    @param T the number of legs
    @param mapping_end an optional argument specifying a mapping on which to
    stop generating
    @param length the maximum number of values to populate each arm with. By
    default this will be N.

    @return a generator of complete mappings.
    '''
    class EndOfSequence(Exception):
        ''' Exception used to signify that mapping_end has been reached.'''
        def __init__(self):
            pass

    def recurse(mapping_start):
        #check for optional end-condition
        if mappingEnd is not None and mapping_start == mappingEnd:
            yield mapping_start
            raise EndOfSequence
        #find the first leg in which the length is less than N.
        shortLeg = 1
        try:
            while len(mapping_start[shortLeg]) >= length:
                shortLeg += 1
        #if we don't find a leg which is too short, the mapping is complete
        #and the recursion is done.
        except IndexError:
            yield mapping_start
            return

        #now shortLeg holds the first leg number which is not large enough.
        #find valid completions of the arm by looking at the lastmost entry in
        #the arm.
        #if the arm is empty, then look at the branch point for completions.
        index = len(mapping_start[shortLeg])
        if index == 0:
            completions = connectivity(mapping_start[0], M, T)
        else:
            completions = connectivity(mapping_start[shortLeg][index-1], M, T)
        #now iterate over those completions
        for c in completions:
            mapping_new = list(mapping_start)
            mapping_new[shortLeg] = mapping_new[shortLeg] + (c,)
            for r in recurse(mapping_new):
                yield r
    #adjust length if called as None
    if length > N:
        raise ValueError("length may not exceed N")
    if length is None:
        length = N
    try:
        for r in recurse(partialMap):
            yield r
    except EndOfSequence:
        return  # done early, mappingEnd has been reached


def completions_surjective(partialMap, N, M, T=3,
                           length=None, endpointMap=None):
    '''
    Generate a series of mappings which are completions of the partial mapping
    mapping_start.

    Generation will continue until the mapping generated is equivalent to
    mapping_end, or until all completions are exhausted if mapping_end is None.

    This mapping is different in that it will attempt to generate only maps
    that are surjective. This should help in processing speed in certain
    scenarios.

    @param mapping_start the partially-complete mapping to iterate over
    @param N the number of nodes per leg in the domain T-od
    @param M the number of nodes per leg in the codomain T-od
    @param T the number of legs
    @param length the maximum number of values to populate each arm with. By
    default this will be N.
    @param endpointMap a list specifying which points map to which endpoints
    for surjectivity assertion

    @return a generator of complete mappings.
    '''
    def dbp(string):
        if DEBUG_PRINT:
            print "***", string

    def recurse(mapping_start, endpoint_map, level=0):
        '''
        The recursive function which does the generation

        1. Find the first leg which is incomplete.
        2. check the endpoint list to determine if any endpoints are to be
        mapped to the undefined portion of that leg.
            a. if not, add an ajacent point and then recusively continue.
            b. if yes, then take the distance between the most recent domain
            point and the one listed in the endpoint map (X), and compare it to
            the distance between that endpoint coordinate and the most recent
            codomain point. (Y)
                i. if X < Y then there is no way for the mapping to connect in
                the way specified. return immediately without yielding.
                ii. If X == Y then connect the points directly and recursively
                continue.
                iii. If X > Y  then we have room to wiggle. Make the next
                codomain point a point connected to the current one, and then
                recursively continue.
        '''
        dbp("")
        dbp("entering recursion level: {}".format(level))
        dbp("mapping_start: {}".format(mapping_start))
        dbp("endpoint_map: {}".format(endpoint_map))
        shortLeg = 1
        try:
            while len(mapping_start[shortLeg]) >= length:
                shortLeg += 1
        #mapping is already complete and we should just return it.
        except IndexError:
            yield mapping_start
            return
        dbp("level {}: found shortLeg={}".format(level, shortLeg))
        index = len(mapping_start[shortLeg])
        dbp("level {}: index number={}".format(level, index))

        endPointNumber = -1
        #check for defined endpoints in this leg.
        for i in range(T):
            arm = endpoint_map[i][0]
            #if any defined endpoints lie on this arm
            if arm == shortLeg-1:
                #if they haven't already been asigned
                dist = endpoint_map[i][1]
                if endPointNumber == -1:
                    endPointNumber = i
                elif dist >= index:
                    #take only the  first-defined point in the empty space.
                    if dist < endpoint_map[endPointNumber][1]:
                        endPointNumber = i
        
        dbp("level {}: endPointNumber={}".format(level, endPointNumber))
        #no endpoints on this leg. Just do a simple recursion lilke before
        if endPointNumber == -1:
            dbp("level {}: No completions found on this arm".format(level))
            if index == 0:
                completions = connectivity(mapping_start[0], M, T)
            else:
                completions = \
                    connectivity(mapping_start[shortLeg][index-1], M, T)
            #now iterate over those completions
            for c in completions:
                mapping_new = list(mapping_start)
                mapping_new[shortLeg] = mapping_new[shortLeg] + (c,)
                for r in recurse(mapping_new, endpoint_map, level=level+1):
                    yield r

        #unassigned endpoint on this arm. This is where things get interesting
        else:
            dbp("level {}: found an endpoint on this arm".format(level))
            endpoint_dist = endpoint_map[endPointNumber][1]
            dbp("level {}: endpoint_dist={}".format(level, endpoint_dist))
            #find distances in both the domain and the codomain.
            X = endpoint_dist - index
            Y = None
            if index == 0:
                Y = Vertex(endPointNumber, M) - mapping_start[0]
            else:
                Y = Vertex(endPointNumber, M) - mapping_start[shortLeg][index-1]
            #now compare X and Y
            dbp("level {}: X={}, Y={}".format(level, X, Y))

            if X == 1 and Y == 0:
                #second conditional is for special case when we are one-off
                #from endpoint index but mapping to endpoint. In this case,
                #we actually do not have room to wiggle.
                ftCurrent = None
                if index == 0:
                    ftCurrent = mapping_start[0]
                else:
                    ftCurrent = mapping_start[shortLeg][index-1]
                completions = [ftCurrent]
                for c in completions:
                    mapping_new = list(mapping_start)
                    mapping_new[shortLeg] = mapping_new[shortLeg] + (c,)
                    for r in recurse(mapping_new, endpoint_map, level=level+1):
                        yield r

            elif X == Y:
                #fill in a direct path between points
                #we need to go in a direction toward the endpoint.
                ftCurrent = None
                if index == 0:
                    ftCurrent = mapping_start[0]
                else:
                    ftCurrent = mapping_start[shortLeg][index-1]
                completions = None

                #if ftCurrent is the branch point, then go up the proper leg.
                if ftCurrent == Vertex(0, 0):
                    completions = [Vertex(endPointNumber, 1)]

                #if ftCurrent is on a different branch than the target
                #endpoint, then go toward the branch point
                elif ftCurrent[0] != endPointNumber:
                    completions = [Vertex(ftCurrent[0], ftCurrent[1]-1)]

                #otherwise we are on the same arm. Go toward the endpoint.
                elif X != 0:
                    completions = [Vertex(ftCurrent[0], ftCurrent[1]+1)]
                else:  # special case when X==Y==0
                    completions = connectivity(ftCurrent, M, T)

                #now sub in the completion and recurse
                for c in completions:
                    mapping_new = list(mapping_start)
                    mapping_new[shortLeg] = mapping_new[shortLeg] + (c,)
                    for r in recurse(mapping_new, endpoint_map, level=level+1):
                        yield r

            elif X < Y:
                #unable to create a surjective map. Return without yielding.
                return

            else:
                #x > Y
                #room to wiggle. Just do a regular completion and recursively
                #continue.
                if index == 0:
                    completions = connectivity(mapping_start[0], M, T)
                else:
                    completions = \
                        connectivity(mapping_start[shortLeg][index-1], M, T)
                #now iterate over those completions
                for c in completions:
                    mapping_new = list(mapping_start)
                    mapping_new[shortLeg] = mapping_new[shortLeg] + (c,)
                    for r in recurse(mapping_new, endpoint_map, level=level+1):
                        yield r

    if length is None:
        length = N
    elif length > N:
        raise ValueError("length may not exceed N")
    elif length == 0:
        yield partialMap
        return

    #check for existance of the endpointMap. If it exists, use it.
    if endpointMap is not None:
        if len(endpointMap) != T:
            raise ValueError("endpointMap is not of the correct size")

        #check to make sure that every defined base point in the list is at
        #least 2M distance away from the others.
        for p1, p2 in combinations(endpointMap, 2):
            if p2 - p1 < 2*M:
                return

        for r in recurse(partialMap, endpointMap):
            yield r

    #check to see if a pre-completion of this map has been performed
    elif partialMap[0].epm is not None:
        epm = partialMap[0].epm
        for r in recurse(partialMap, epm):
            yield r

    #otherwise, we need to generate every endpointMap from scratch.
    else:
        points = [Vertex(0, 0)]
        for arm in range(0, T):
            for t in range(1, N+1):
                points.append(Vertex(arm, t))
        #take every three-permutation of points
        for epm in permutations(points, 3):
            #if we're trying to map the basepoint to and endpoint and it isn't
            #already there, then skip this permutation
            #also enforce proper seperation of endpoint terms.
            try:
                for p1, p2 in combinations(epm, 2):
                    if p2 - p1 < 2*M:
                        raise ValueError
                for arm in range(3):
                    if epm[arm] == Vertex(0, 0) and \
                       partialMap[0] != Vertex(arm, M):
                        raise ValueError
            except ValueError:
                continue

            for r in recurse(partialMap, epm):
                #if we are pre-completing, then set the epm in the base point
                #to be retrieved later.
                if length > 0:
                    r[0].epm = epm
                yield r


def functionize(mapping, N, M, T=3):
    '''
    Generate a function object assosciated with the supplied triod mapping.

    The returned function may be called with arguments as a tuple of (arm, t),
    where arm is the index of the domain arm, and t is the position on that
    arm, with 0 being the branch point, and 1 being the end point of the arm.
    The mapping used to generate the function will be saved as the f.mapping
    member variable.

    @param mapping the triod mapping used to generate the function
    @param N the number of nodes per leg in the domain triod
    @param M the number of onodes per leg in the codomain triod
    @param T the number of legs
    @return A function object representing that mapping.
    '''
    def mappingDereference(mapping, N, M, point):
        #point is in non-normalized tuple form
        arm, vertex = point
        #find nearest integers to vertex
        vLow = int(vertex)
        vHigh = int(vertex+1)
        if vHigh > N:  # gone past endpoint, therefore vertex is the endpoint
            vHigh = N
        #dereference vLow
        if vLow == 0:  # look at branchpoint
            fLow = mapping[0][1]
        else:
            fLow = mapping[arm+1][vLow-1][1]
        #dereference vHigh
        fHigh = mapping[arm+1][vHigh-1][1]
        #find the arm that the new point now resides on
        fArm = mapping[arm+1][vHigh-1][0]
        #decimal portion of vertex indicates where it lies between fLow and
        #fHigh.
        vP = vertex % 1.0
        #now go uP distance from fLow to fHigh. If order of fHigh, fLow is
        #reversed, then we need to subtract rather than add.
        if fLow < fHigh:
            f = fLow + vP
        elif fLow == fHigh:
            f = fLow
        else:
            f = fLow - vP
        #the zero point should always lie on the zero-arm for testing purposes.
        if f == 0:
            fArm = 0
        return Point(fArm, f)

    f = lambda point: mappingDereference(mapping, N, M, point)
    f.mapping = mapping
    return f


def connectivity(pt, N, T=3):
    '''
    Generate a list of points ajacent to the point specified in the argument.
    Points will always be in a well-defined order, as follows:
    - the point itself
    - point(s) closer to the branch point
    - point(s) farther from the branch point
    If the point supplied is the branch point, then points will be supplied in
    order of decreasing index.

    @param pt: the point tuple for which to generate the connectivity
    map.
    @param N: the number of points per leg of the T-od
    @param T: the number of legs of the T-od

    @return a tuple of points ajacent to the given point in tuple form.
    '''
    arm, t = pt
    #special case for the branch point
    if t == 0:
        return (Vertex(0, 0),) + tuple(Vertex(i, 1) for i in range(T))
    #endpoint condition
    elif t == N:
        return (Vertex(pt), Vertex(arm, t-1))
    else:
        return (Vertex(pt), Vertex(arm, t-1), Vertex(arm, t+1))


def linspace(start, stop, n):
    '''
    creates a linspace of n divisions in the interval [start, stop]
    '''
    if n == 1:
        yield stop
        return
    h = (stop - start) / (n - 1)
    for i in range(n):
        yield start + h * i

if __name__ == "__main__":
    from comparitors import checkSurjectivity as csj
    n, m = 6, 3 
    #there should only be one valid completion for this one.
    mapping = (Vertex(0, 2), (), (), ())
    endpts = (Vertex(0, 4), Vertex(1, 4), Vertex(2, 4))
    partialLength = 1
    for c_partial in completions(mapping, n, m, length=partialLength):
        print "partial: {}".format(c_partial)
        for c in completions_surjective(c_partial, n, m, endpointMap=None):
            print "---"
            print c
            if csj(c, n, m):
                print 'pass'
            else:
                print 'fail'
    print "DONE"
