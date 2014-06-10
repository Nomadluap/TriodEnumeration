'''
Created on Jun 9, 2014

@author: paul
'''
import unittest
from comparitors import checkPartialDisjointness as cpd
from T_od import Point as p


class Test(unittest.TestCase):


    def test_basePoint(self):
        '''
        Test to make sure that any two mappings which share a basepoint will
        be caught correctly
        '''
        N, M, T = 3, 3, 3
        map1 = (p(0, 0), (), (), ())
        self.assertFalse(cpd(map1, map1, N, M, T))
        map2 = (p(2, 0), (), (), ())
        self.assertFalse(cpd(map1, map2, N, M, T))

    def test_crossing(self):
        '''
        Test to make sure that cpd catches non-disjointness when two points
        cross eachother.
        '''
        N, M, T = 3, 3, 3
        map1 = (p(0, 0), (p(0, 1), p(0, 2), p(0, 3)), (), () )
        map2 = (p(0, 3), (p(0, 2), p(0, 1), p(0, 0)), (), () )
        #the maps cross at (0, 1.5)
        self.assertFalse(cpd(map1, map2, N, M, T))
    def test_following(self):
        '''
        Make sure cpd does not flag the occasion where one map follows behind 
        the other map.
        '''
        N, M, T = 3, 3, 3
        #map2 follows map1
        map1 = (p(0, 0), (p(1, 1), p(1, 2), p(1, 3)), (), ())
        map2 = (p(2, 1), (p(2, 0), p(1, 1), p(1, 2)), (), ())
        self.assertTrue(cpd(map1, map2, N, M, T))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()