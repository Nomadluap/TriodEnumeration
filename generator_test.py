import generators
from comparitors import checkSurjectivity
from overseer import generate_basepoints
'''
A test to ensure that the surjective generator generates all of the completions
it can.
'''
N, M, T = 4, 2, 3


def main():
    basepoints = generate_basepoints() 
    aCount = 0
    bCount = 0
    for point in basepoints:
        mapp = [point, tuple(), tuple(), tuple()]
        for comp in generators.completions(mapp, N, M, T):
            if checkSurjectivity(comp, N, M, T):
                aCount += 1
        for comp in generators.completions_surjective(mapp, N, M, T):
            bCount += 1
        print "aCount ", aCount
        print "bCount ", bCount
        print ""

    print "aCount ", aCount
    print "bCount ", bCount

if __name__ == "__main__":
    print "begin"
    main()
