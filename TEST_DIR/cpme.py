
#from singleton_decorator import singleton

#@singleton
class A:
    def __init__(self):
        print ("A INITED")

    a= {}
    def add(self, key, value):
        if key not in self.a:
            self.a[key] = None
        self.a[key] = value
        print(self.a)



import timeit
t = timeit.timeit('"-".join(str(n) for n in range(100))', number=10000)
print(t)

""" a = A()
b = A()
a.add('g',45)
 """
