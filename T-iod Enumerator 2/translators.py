'''
Created on Jun 3, 2014
A collection of functions which translate from one coordinate space to another

@author: paul
'''
from __future__ import division
#There are three types of coordinate to translate between.
#first, there is the integer index space, where points on the triod are in the
#form 0<=t<=3*N*T, where T is the number of legs and N is the number of points
#per arm.
#The second is a tuple of the form (leg, vertex), where 0<=leg<T, 0<=vertex<=N
#the third is a (leg, t) tuple where 0<=leg<T, 0.0 <= t <= 1.0

#the first form will be called the index form. The second form will be called
#the tuple form, and the third form will be the normalized tuple form. 


def index2Tuple(index, N):
    '''
    Convert an index-form of a coordinate to the tuple form.

    @param index the index to convert
    @param N the number of points per leg of the T-od

    @return the (arm, vertex) pair
    '''
    #first, if the index is zero, return the zero-tuple
    if index == 0:
        return (0, 0)
    #now find arm
    arm = index // N
    if index % arm == 0:
        arm -= 1
    #now the vertex is the remainder of the division
    vertex = index % N

    return (arm, vertex)

def tuple2index(tup, N):
    '''
    Convert an (arm, vertex) tuple to an integer index

    @param tup the tuple to convert
    @param N the number of points per arm of the T-od

    @return the index representing the tuple.
    '''
    arm, vertex = tup
    #if the vertex is zero, then the index is zero, regardless of the arm
    if vertex == 0:
        return 0
    index = arm * N + vertex
    return index
def tuple2Normed(tup, N):
    '''
    Convert a tuple to its normalized counterpart, so that 0<=vertex<=1
    
    @param tup the tuple to convert
    @param N the number of points per leg of the T-od
    @return the normalized tuple
    '''
    arm , vertex = tup
    t = vertex / N
    return (arm, t)

def normed2Tuple(tup, N):
    '''
    convert a normalized tuple to its regular counterpart, so that 0<=vertex<=N

    @param tup the tuple to convert
    @param N the number of points per leg of the T-od

    @return the scaled tuple
    '''
    arm, t = tup
    vertex = t * N
    return (arm, vertex)

def index2Normed(index, N):
    '''
    Convert a point index to a normed tuple form
    
    @param index the index of the point
    @param N the number of points per leg of the T-od

    @return the normed tuple representation of the indexed point
    '''
    return tuple2Normed(index2Tuple(index, N), N)

def Normed3Index(tup, N):
    '''
    Convert a normed tuple to its index representation

    @param tup the normed tuple to convert
    @param N the number of points per leg of the T-od

    @return the index representing the point
    '''
    return tuple2Index(Normed2Tuple(tup, N), N)


