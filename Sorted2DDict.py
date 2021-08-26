# Version 3.6.1


class Sorted2DDict:
    def __init__(self):
        self._data = {}

    def __sort(self,dic):
        dic_sorted = sorted(dic.items())
        return {k:v for k,v in dic_sorted}

    def update(self,expiry, strike, value):
        if expiry in self._data:
            if strike in self._data[expiry]:
                self._data[expiry][strike] = value
            else:
                # Adding a new strike, needs to sort
                self._data[expiry][strike] = value
                self._data[expiry] = self.__sort(self._data[expiry])
        else:
            # Adding a new expiry, needs to sort
                self._data[expiry] = {}
                self._data[expiry][strike] = value
                self._data = self.__sort(self._data)
        return self._data
