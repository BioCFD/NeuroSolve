from abc import ABC, abstractmethod


class CaseFeature(ABC):
    '''
    Abstract class represent any case feature, such as turbulence, time, ...
    '''
    def __init__(self, case):
        self._case = case

    def _update_bcs(self):
        pass

    def _update_system(self):
        pass

    def _update_constant(self):
        pass

    def correct(self):
        self._update_bcs()
        self._update_constant()
        self._update_system()

    def case(self):
        return self._case