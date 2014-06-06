'''
This file contains global definitions that are common to all files. 

Created on Jun 6, 2014

@author: paul
'''

class Point(object):
    '''
    A class which abstracts a tuple. In basic usage, it is used simply to 
    overload the __eq__ operator, so that tuple-based points handle the 
    base point correctly. 
    '''
    def __init__(self, arm, vertex):
        '''
        Construct a point using (arm, vertex) tuple elements. 
        '''
        self.pt = (arm, vertex)
    
    def __eq__(self, y):
        '''
        True if and only if x == y
        '''
        #additionally true iff both coords are at zero, regardless
        #of arm. 
        if self.pt[1] == y.pt[1] == 0:
            return True
        else:
            return self.pt == y.pt
    
    def __getitem__(self, k):
        '''
        passthough for array indexing
        '''
        return self.pt[k]
    
    def __str__(self):
        return "Point" + str(self.pt)
    
    def __repr__(self):
        return self.__str__()