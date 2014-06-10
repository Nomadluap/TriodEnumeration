'''
Created on Jun 6, 2014

@author: paul
'''
import unittest
from generators import connectivity as con
from T_od import Point as p


class Test_connectivity(unittest.TestCase):


    def test_1(self):
        '''
        test connectivity for triods of size 1
        '''
        N = 1
        self.assertEqual(con(p(0, 0), N),( p(0, 0), p(0, 1), p(1, 1), p(2, 1) ))
        for t in range(3):
            self.assertEqual(con(p(t, 1), N), (p(t, 1), p(0, 0))) 
    def test_2(self):
        '''
        test connectivity for triods of size 2
        '''
        N = 2
        #test branch point
        branchmap = ( p(0, 0), p(0, 1), p(1, 1), p(2, 1) )
        self.assertEqual(con(p(0, 0), N), branchmap)
        #test midpoint
        for t in range(3):
            midmap = ( p(t, 1), p(t, 0), p(t, 2))
            self.assertEqual(con(p(t, 1), N), midmap)
        #test endpoints
        for t in range(3):
            endmap = ( p(t, 2), p(t, 1))
            self.assertEqual(con(p(t, 2), N), endmap)
    
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_1']
    unittest.main()