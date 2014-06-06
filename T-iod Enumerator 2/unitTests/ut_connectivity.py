'''
Created on Jun 6, 2014

@author: paul
'''
import unittest
from generators import connectivity as con
from comparitors import equals


class Test(unittest.TestCase):


    def test_1(self):
        '''
        test connectivity for triods of size 1
        '''
        N = 1
        self.assertEqual(con((0, 0), N),( (0, 0), (0, 1), (1, 1), (2, 1) ))
        for t in range(3):
            self.assertTrue(equals(con((t, 1), N), ((t, 1), (0, 0))) )


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_1']
    unittest.main()