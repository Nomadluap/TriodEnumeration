'''
Created on Jun 9, 2014

@author: paul
'''
import unittest
from T_od import Point as p
from comparitors import checkCommutativity as ccm



class Test_checkCommutativity(unittest.TestCase):


    def test_doubleIdentity(self):
        '''
        Test the ccm for double identity functions. It should pass.
        '''
        N, M, T = 3, 3, 3
        iden = (p(0, 0), (p(0, 1), p(0, 2), p(0, 3)), (p(1, 1), p(1, 2), p(1, 3)), (p(2, 1), p(2, 2), p(2, 3)))
        self.assertTrue(ccm(iden, iden, N, M, T))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()