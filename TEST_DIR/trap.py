import signal
import sys
import time

import threading

def handle():
    while (True):
        x = input("Listening\n")
        print (" HERE WE GO - ", x, "\n")


t = threading.Thread(target=handle,)
t.start()

class A():
    def __init__(self, val = 'col'):
        self._col = val

a = A('A')
b = A('B')

trap_last_time = None
def received_ctrl_c(signum, stack):
    global trap_last_time
    print("Received Ctrl-C")
    now = time.time()
    if (trap_last_time is None):
        trap_last_time = now
    elif (now - trap_last_time < 3):
        sys.exit(0)
    trap_last_time = now
    print(a._col)

handler = signal.signal(signal.SIGINT, received_ctrl_c)
while True:
    print("Waiting…")
    time.sleep(5)
