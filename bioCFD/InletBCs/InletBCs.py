import os
import sys
from abc import ABC, abstractmethod
from string import Template

from bioCFD.Cases.CaseFeature import CaseFeature
from bioCFD.tools import update_OFdict
from bioCFD.templates import INLET_U

class InletBC(CaseFeature):

    def __init__(self, case, field):
        self._field = field
        super().__init__(case)

    def field(self):
        return self._field
    
    def value(self):
        f = self._field
        return self.case().case_dict()['inletBC'][f]['value']

    @classmethod
    def select(cls,case):
        fields = [*case.case_dict()['inletBC']]
        names = [case.case_dict()['inletBC'][f]['type'] for f in fields]
        print(f'Selected Bcs {fields}, {names}')
        bcs = {}
        for f, name in zip(fields, names):
            subtype = [st for st in cls.__subclasses__() if st.__name__ == name]
            if len(subtype) == 0:
                names = [st.__name__ for st in cls.__subclasses__()]
                print(f'\t\n Type {name} not found, select one of {names}')
                sys.exit(1)
            bcs[f] = subtype[0](case, f)
        return bcs


class Fixed(InletBC):

    def __init__(self, case, field):
        super().__init__(case, field)

    def _update_bcs(self):
        zero = self.case().zero()
        f = self.field()
        value = self.value()

        _ = update_OFdict(
            os.path.join(zero, f),
            'Uinlet',
            f'{value}'
        )

class Profile(InletBC):

    def __init__(self, case, field):
        super().__init__(case, field)
        if self.field() != 'U':
            raise NotImplementedError(
            f'Profile type BC is implemented for U only not for {self.field()}')

    def _update_bcs(self):
        zero = self.case().zero()
        f = self.field()
        file_name = self.value()
        
        temp_pro = Template(INLET_U)
        value = temp_pro.safe_substitute({"FILE_NAME":file_name})
        # value =f'"{value}"'
        _ = update_OFdict(
            os.path.join(zero, f),
            'boundaryField.inlet',
            f' \' {value} " \' '
        )
        