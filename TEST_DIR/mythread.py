#import commonclass as cc
import threading, time
import time

def handle(key, value):
    pass

def a(key, value):
    handle(key,value)



def example():
    lst = ['a','b',]
    i = 6
    while i >= 0:
        threads = []
        for c in lst:
            c0 = time.perf_counter()
            t = threading.Thread(target=a,args=(c,i,))
            c1 = time.perf_counter()
            t.start()
            spend2 = c1 - c0
            print("perf_counter() time: {}s".format(spend2))
            threads.append(t)
        for t in threads:
            t.join()
        i = i-1

c0 = time.perf_counter()
example()
c1 = time.perf_counter()
spend2 = c1 - c0
print("perf_counter() time: {}s".format(spend2))
