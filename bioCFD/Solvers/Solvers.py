import os
import sys
from shutil import copyfile
from bioCFD.Cases.CaseFeature import CaseFeature
from bioCFD.tools import update_OFdict, run_system

class Solver(CaseFeature):

    def __init__(self, case):
        super().__init__(case)
        self._name = None
        self._started = False

    def started(self):
        return self._started

    @classmethod
    def select(cls, case):

        name = case.case_dict()['solver']['type']
        subtype = [st for st in cls.__subclasses__() if st.__name__ == name]
        if len(subtype) == 0:
            names = [st.__name__ for st in cls.__subclasses__()]
            print(f'\t\n Type {name} not found, select one of {names}')
            sys.exit(1)

        return subtype[0](case)

    def _update_schemes(self):
        
        ext = self._name
        src = os.path.join(self.case().system(), f'fvSchemes.{ext}')
        dst = os.path.join(self.case().system(), 'fvSchemes')
        copyfile(src, dst)

    def _update_solution(self):

        ext = self._name
        src = os.path.join(self.case().system(), f'fvSolution.{ext}')
        dst = os.path.join(self.case().system(), 'fvSolution')
        copyfile(src, dst)

    def _update_control(self):

        ext = self._name
        src = os.path.join(self.case().system(), f'controlDict.{ext}')
        dst = os.path.join(self.case().system(), 'controlDict')
        copyfile(src, dst)

    def _update_system(self):
        self._update_schemes()
        self._update_solution()
        self._update_control()
        super()._update_system()

class Steady(Solver):

    def __init__(self, case):
        super().__init__(case)
        self._name = 'steady'

    def run(self):
        if not self.case().finished():
            n = self.case().nproc()
            print('\tRunning simpleFoam\n')
            self._started = True
            self.case().update_state()
            _ = run_system(
                f"mpirun -np {n} simpleFoam -parallel > log.simpleFoam",
                cwd=self.case().path())
            _ = run_system(
                f"reconstructPar > log.reconstructPar",
                cwd=self.case().path())                

class Unsteady(Solver):

    def __init__(self, case):
        super().__init__(case)
        self._name = 'unsteady'

    def run(self):
        if not self.case().finished():
            n = self.case().nproc()
            print('\tRunning pimpleFoam\n')
            self._started = True
            self.case().update_state()
            _ = run_system(
                f"mpirun -np {n} pimpleFoam -parallel > log.pimpleFoam",
                cwd=self.case().path())
            _ = run_system(
                f"reconstructPar > log.reconstructPar",
                cwd=self.case().path())                   
    
    def _update_control(self):

        super()._update_control()
        if 'period' in self.case().case_dict()['solver']:
            period = self.case().case_dict()['solver']['period']
        else:
            period = 0.83

        if 'n_cycles' in self.case().case_dict()['solver']:
            n_cycles = self.case().case_dict()['solver']['n_cycles']
        else:
            n_cycles = 5

        end_time = period * n_cycles
        cdict = os.path.join(self.case().system(), 'controlDict')
        _ = update_OFdict(cdict, 'endTime', end_time)