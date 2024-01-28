import os
import sys
from abc import ABC, abstractmethod


from bioCFD.Cases.CaseFeature import CaseFeature
from bioCFD.tools import update_OFdict

class ViscosityModel(CaseFeature):

    def __init__(self, case):
        super().__init__(case)

    @classmethod
    def select(cls, case):

        name = case.case_dict()['viscosityModel']['type']
        subtype = [st for st in cls.__subclasses__() if st.__name__ == name]
        if len(subtype) == 0:
            names = [st.__name__ for st in cls.__subclasses__()]
            print(f'\t\n Type {name} not found, select one of {names}')
            sys.exit(1)

        return subtype[0](case)

class Newtonian(ViscosityModel):

    def __init__(self, case):
        super().__init__(case)

    def _update_constant(self):
        trans_dict = os.path.join(self.case().constant(), 'transportProperties')
        _ = update_OFdict(trans_dict, 'transportModel', 'Newtonian')

        nu = f"nu [ 0 2 -1 0 0 0 0 ] {self.case().case_dict()['viscosityModel']['nu']}"
        nu = f'"{nu}"'
        _ = update_OFdict(trans_dict, 'nu', f'{nu}')
        super()._update_constant()


class NonNewtonian(ViscosityModel):

    def __init__(self, case):
        super().__init__(case)
        if self.case().case_dict()['viscosityModel']['name']:
            self._model = self.case().case_dict()['viscosityModel']['name']
        else:
            self._model = 'CrossPowerLaw'

        
        
    def _update_constant(self):
        trans_dict = os.path.join(self.case().constant(), 'transportProperties')
        _ = update_OFdict(trans_dict, 'transportModel', self._model)
        super()._update_constant()