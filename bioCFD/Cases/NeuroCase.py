import os
import numpy as np
import shutil
from distutils.dir_util import copy_tree

from bioCFD.tools import update_OFdict, run_system
from bioCFD.Meshes.Mesh import *
from bioCFD.Cases.Case import Case

class NeuroCase(Case):

    def __init__(self, case_path, case_dict, state_dict=None, overwrite=False):
        super().__init__(case_path, case_dict, state_dict=state_dict, 
            overwrite=overwrite)
    
    def initialise(self, case=None):
        if not self._initialised:
            print(f"\tCreate case {self.path()}\n")

            temp_case = os.path.join(os.environ["BIOCFD_TEMP"], "NeueroCase")
            copy_tree(temp_case, self.path())
            super().initialise()

    def correct(self):
        if not self._corrected:
            zero_org = os.path.join(self.path(), "0.org")
            #change it later for init from case
            if os.path.exists(self.zero()):
                shutil.rmtree(self.zero())
            shutil.copytree(zero_org, self.zero())
            super().correct()