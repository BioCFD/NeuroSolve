from bioCFD.Solvers.Solvers import Solver
from bioCFD.TurbulenceModels.TurbulenceModels import TurbulenceModel
from bioCFD.ViscosityModels.ViscosityModels import ViscosityModel
from bioCFD.InletBCs.InletBCs import InletBC
from bioCFD.Cases.CaseFeature import CaseFeature


class CaseSetup(CaseFeature):

    def __init__(self, case):

        self._features = \
        {
            "solver": Solver.select(case),
            "turbulenceModel": TurbulenceModel.select(case),
            "viscosityModel": ViscosityModel.select(case),
            "inletBCs": InletBC.select(case)
        }
    
    def features(self):
        return self._features
        
    def correct(self):

        for key, value in self._features.items():
            print(f'Setup case feature {key}')
            if isinstance(value, dict):
                for skey, svalue in value.items():
                    svalue.correct()
            else:
                value.correct()