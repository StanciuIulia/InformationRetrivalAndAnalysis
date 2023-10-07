#!/usr/bin/env python
"""
Testing LSH in comparison with BFH
@author: iulia.stanciu 
"""

import sys
import argparse
import lsh
import bfh
from sklearn.metrics import balanced_accuracy_score, accuracy_score


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', default=10, type=int)
    parser.add_argument('-m', default=5, type=int)
    args = parser.parse_args()

    print("Running lsh.py with parameters k =", args.k, "and m =", args.m)
    me = lsh.lsh(args.k, args.m)
    
    print("Running bfh.py")
    me2 = bfh.bfh()
    
    expected = []
    lsh_returned = []
    
    for r in range(1500, len(me.data)):
        im = me.data[r]
        im2 = me.data[r]
        cands = me.candidates(im)
        print("there are %4d candidates for image %4d" % (len(cands), r))
        
        lsh_nn = me.nearest_neighbor(im)
        #print (lsh_nn)
        bf_nn = me2.brute_force_search(im2)
        #print(bf_nn)
        
        if (lsh_nn != bf_nn):
            print (lsh_nn)
            print(bf_nn)
        
        expected.append(bf_nn[1])
        if(cands):
            lsh_returned.append(lsh_nn[1])
        else:
            lsh_returned.append(-1)
    
    print("Accuracy is: ", accuracy_score(expected, lsh_returned))
    print("Balanced accuracy is: ", balanced_accuracy_score(expected, lsh_returned))
    
    return


if __name__ == "__main__":
    sys.exit(main())
