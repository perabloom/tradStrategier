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
