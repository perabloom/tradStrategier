# Version 3.6.1
from Sorted2DDict import *
from tia_utils_internal import *

class OptionHolder:
    def __init__(self):
        self._puts = Sorted2DDict()
        self._calls = Sorted2DDict()

    def __pretty(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key))
            if isinstance(value, dict):
                self.__pretty(value, indent+1)
            else:
                print('\t' * (indent+1) + str(value))


    def add(self, OCC, info):
        option = get_option_from_occ(OCC)
        if (option['option_type'] == 'P'):
            self._puts.update(option['expiry'], option['strike'], info)
        elif (option['option_type'] == 'C'):
            self._calls.update(option['expiry'], option['strike'], info)
        else:
            raise Exception("Unknown option Type", option['option_type'])

    def printPuts(self):
        self.__pretty(self._puts._data)

    def printCalls(self):
        self.__pretty(self.__calls._data)

def example():
    a = OptionHolder()
    a.add("SNDL210730P00002000", "ASDF")
    a.printPuts()

#example()
