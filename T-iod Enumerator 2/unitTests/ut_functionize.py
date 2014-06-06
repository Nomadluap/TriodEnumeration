'''
Created on Jun 6, 2014

@author: paul
'''
from __future__ import division
import unittest
from generators import functionize, linspace
from comparitors import equals



class TestFunctionize(unittest.TestCase):

    def setUp(self):
        self.N = 3
        self.M = 3
        self.T = 3



    def tearDown(self):
        pass


    def test_identity(self):
        '''
        Test the identity map to ensure that all points map to themselves
        '''
        #mapping is a simple identity map
        identity = ((0, 0), ((0, 1), (0, 2), (0, 3)), ((1, 1), (1, 2), (1, 3)), ((2, 1), (2, 2), (2, 3)))
        id = functionize(identity, self.N, self.M, self.T)
        #test 100 points over each arm
        for arm in range(self.T):
            for t in linspace(0, self.N, 50):
                point = (arm, t)
                self.assertTrue(equals(point, id(point) ))
        #test the key points
        for arm in range(self.T):
            for t in range(1, self.N+1):
                point = (arm, t)
                self.assertTrue(equals(point, id(point) ))
                
    def test_rotation(self):
        '''
        Test a simple 'rotation' map to ensure that all points map to
        themselves, only one arm over
        '''
        mapping = ((0, 0), ((1, 1), (1, 2), (1, 3)), ((2, 1), (2, 2), (2, 3)), ((0, 1), (0, 2), (0, 3)))
        f = functionize(mapping, self.N, self.M, self.T)
        #test 100 points over each arm
        for arm in range(self.T):
            for t in linspace(0, self.N, 50):
                point = (arm, t)
                self.assertTrue(equals(((arm+1)%self.T, t), f(point) ))
        #test the key points
        for arm in range(self.T):
            for t in range(1, self.N+1):
                point = (arm, t)
                self.assertTrue(equals(((arm+1)%self.T, t), f(point) ))
                
    def test_tripleRotation(self):
        '''
        A triple-rotation should yield the identity function
        '''
        mapping = ((0, 0), ((1, 1), (1, 2), (1, 3)), ((2, 1), (2, 2), (2, 3)), ((0, 1), (0, 2), (0, 3)))
        f = functionize(mapping, self.N, self.M, self.T)
        #test 100 points over each arm
        for arm in range(self.T):
            for t in linspace(0, self.N, 50):
                point = (arm, t)
                self.assertTrue(equals(point, f(f(f(point))) ))
        #test the key points
        for arm in range(self.T):
            for t in range(1, self.N+1):
                point = (arm, t)
                self.assertTrue(equals(point, f(f(f(point))) ))
    
    def test_armTransition(self):
        '''
        Make sure functionize works correctly when going from one arm to 
        another.
        '''
        mapping = ( (0, 2), ((0, 3), (0, 3), (0, 3)), ((0, 1), (0, 0), (1, 1)),  ((0, 3), (0, 3), (0, 3)) )
        f = functionize(mapping, self.N, self.M, self.T)
        #make sure branch point maps correctly
        self.assertEqual((0, 2), f((0, 0)) )
        #now follow the second leg and make sure the points line up as they should
        self.assertEqual(f((1, 1)), (0, 1))
        self.assertEqual(f((1, 2)), (0,0))
        self.assertEqual(f((1, 3)), (1, 1))
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()