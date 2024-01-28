import os
import sys
from abc import ABC, abstractmethod


from bioCFD.Cases.CaseFeature import CaseFeature
from bioCFD.tools import update_OFdict

class TurbulenceModel(CaseFeature):

    def __init__(self, case):
        super().__init__(case)

    @classmethod
    def select(cls,case):

        name = case.case_dict()['turbulenceModel']['type']
        subtype = [st for st in cls.__subclasses__() if st.__name__ == name]
        if len(subtype) == 0:
            names = [st.__name__ for st in cls.__subclasses__()]
            print(f'\t\n Type {name} not found, select one of {names}')
            sys.exit(1)

        return subtype[0](case)

class Laminar(TurbulenceModel):

    def __init__(self, case):
        super().__init__(case)

    def _update_constant(self):

        tur_dict = os.path.join(self.case().constant(), 'turbulenceProperties')
        _ = update_OFdict(tur_dict, 'simulationType', 'laminar')
        
        super()._update_constant()

class RANS(TurbulenceModel):

    def __init__(self, case):
        super().__init__(case)

    def _update_constant(self):

        tur_dict = os.path.join(self.case().constant(), 'turbulenceProperties')
        _ = update_OFdict(tur_dict, 'simulationType', 'RAS')

        super()._update_constant()

class LES(TurbulenceModel):

    def __init__(self, case):
        super().__init__(case)

    def _update_constant(self):

        tur_dict = os.path.join(self.case().constant(), 'turbulenceProperties')
        _ = update_OFdict(tur_dict, 'simulationType', 'LES')

        super()._update_constant()