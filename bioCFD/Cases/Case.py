import os
import json
from abc import ABC, abstractmethod

from bioCFD.Cases.CaseSetup import CaseSetup
from bioCFD.Meshes.Mesh import Mesh
from bioCFD.tools import update_OFdict, run_system




class Case(ABC):
    '''
    Abstract base clase
    '''

    def __init__(self, case_path, case_dict, state_dict=None, overwrite=False):

        self._case_dict = case_dict
        self._path = os.path.join(case_path)
        self._mesh = Mesh.select(self)
        self._setup = CaseSetup(self)
        self._state_dict = state_dict
        self._overwrite = overwrite
        self._load_state()

    def _load_state(self):

        if self._state_dict==None or self._overwrite:
            self._decomposed = False
            self._corrected = False
            self._initialised = False
            self._finished = False
            self._mesh._meshed = False

        else:
            st = self._state_dict
            solver = self._setup.features()['solver']
            self._mesh._meshed = st['meshed'] if 'meshed' in st else False
            self._decomposed = st['decomposed'] if 'decomposed' in st else False
            self._initialised = st['initialised'] if 'initialised' in st else False
            self._corrected = st['corrected'] if 'corrected' in st else False
            self._finished = st['finished'] if 'finished' in st else False
            solver._started = st['started'] if 'started' in st else False

    def finished(self):
        return self._finished
           
    def path(self):
        return self._path

    def constant(self):
        return os.path.join(self.path(),'constant') 

    def system(self):
        return os.path.join(self.path(),'system') 

    def zero(self):
        return os.path.join(self.path(),'0')

    def case_dict(self):
        return self._case_dict
    
    def _clean(self):
        '''
        clean OpenFOAM template case
        '''
        pass

    @abstractmethod
    def initialise(self, case=None):
        '''
        Copy template or from existing case
        '''
        self._clean()
        self._initialised = True
        self.update_state()


    def run(self, case=None):

        if not self._corrected:
            self.correct()
            
        if not self.decomposed():
            self.decompose()
        solver = self._setup.features()['solver']
        solver.run()
        self._finished = True
        self.update_state()


    def generate_mesh(self):
        self._mesh.generate()
        self.update_state()

    def decompose(self):
        '''
        force decomposition of the case, careful here! 
        '''
        if not self._decomposed:
            dedict = os.path.join(self.path(), "system", "decomposeParDict")

            _ = update_OFdict(dedict, "numberOfSubdomains", self.nproc())
            print('\tRunning decomposePar\n')
            _ = run_system(
                "decomposePar -force | tee log.decomposePar",
                cwd=self.path())

            self._decomposed = True
            self.update_state()

    def decomposed(self):
        return self._decomposed
    
    def nproc(self):
        return self.case_dict()['nproc']

    def correct(self):
        self._setup.correct()
        self._corrected = True
        self.update_state()
        
    def update_state(self):
        
        state_file = os.path.join(self.path(), 'state.json')
        solver = self._setup.features()['solver']
        state_dict = {
            'meshed' : self._mesh.meshed(),
            'decomposed' :  self._decomposed,
            'initialised' : self._initialised,
            'corrected' : self._corrected,
            'started' : solver.started(),
            'finished' : self._finished
        }

        with open(state_file,'w') as out:
            json.dump(state_dict, out, indent=4)



