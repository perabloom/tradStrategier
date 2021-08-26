import threading, queue, time


def a(g):
    time.sleep(5)
    print("Function a is running at time: " + str(int(time.time())) + " seconds." + g)

def b():
    print("Function b is running at time: " + str(int(time.time())) + " seconds.")

threading.Thread(target=a,args=('d',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
threading.Thread(target=a,args=('3',)).start()
