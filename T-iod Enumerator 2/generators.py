'''
Created on Jun 3, 2014

Functions for triod enumeration which generate things, including funciton
and mapping generators.

@author: paul
'''
from T_od import Point

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
        raise ValueError, "length may not exceed N"
    if length is None:
        length = N
    try:
        for r in recurse(partialMap):
            yield r
    except EndOfSequence:
        return #done early, mappingEnd has been reached
            
def functionize(mapping, N, M, T=3):
    '''
    Generate a function object assosciated with the supplied triod mapping. 
    
    The returned function may be called with arguments as a tuple of 
    (arm, t), where arm is the index of the domain arm, and t is the position 
    on that arm, with 0 being the branch point, and 1 being the end point of the
    arm. The mapping used to generate the function will be saved as the
    f.mapping member variable.
    
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
        if vHigh > N: #gone past endpoint, therefore vertex is the endpoint
            vHigh = N
        #dereference vLow
        if vLow == 0: #look at branchpoint
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
        return (Point(0, 0),) + tuple(Point(i, 1) for i in range(T))
    #endpoint condition
    elif t == N:
        return (Point(pt), Point(arm, t-1))
    else:
        return (Point(pt), Point(arm, t-1), Point(arm, t+1))
    
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
    n, m = 3, 2
    mapping = (Point(0, 0), (), (), ())
    for c in completions(mapping, n, m, length=1):
        print c
        
        
            