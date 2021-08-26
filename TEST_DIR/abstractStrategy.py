from abc import ABC, abstractmethod

class ABSTRACT_STRATEGY(ABC):

    @abstractmethod
    def getProcessor(self):
        pass

    @abstractmethod
    def getBroker(self):
        pass

    @abstractmethod
    def filterOut(self,data):
        pass

    @abstractmethod
    def handle(self,data):
        pass



class B(ABSTRACT_STRATEGY):
    def getProcessor(self):
        print("DSF")

    def getBroker(self):
        print("DSF")

    def filterOut(self,data):
        print("DSF")

    def handle(self,data):
        print("DSF")


x = B()
x.getBroker()
