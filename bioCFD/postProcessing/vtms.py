import os
import json
import pyvista as pv


class VTM():

    def __init__(self, vtm_file):
        self._vtm_file = vtm_file

        self._load()

    def _load(self):
        self._vtm_data = pv.read(self._vtm_file)
    
    def internal(self):
        return self._vtm_data['internal']

    def boundary(self):
        return self._vtm_data['boundary']

    def time(self):
        return self.internal()['TimeValue'][0]

    def data(self):
        return self._vtm_data


class VTMS():

    def __init__(self, vtms_file):
        self._vtms_file = vtms_file

        self._load()

    def _load(self):

        with open(self._vtms_file, 'r') as instream:
            self._vtms_dict = json.load(instream)
        
        print(f'\tAvilable data \n {json.dumps(self._vtms_dict["files"], indent=4)}\n')

        base_dir = os.path.dirname(self._vtms_file)
        self._vtm_files = [os.path.join(base_dir,f["name"]) for f in self._vtms_dict["files"]]

    
    def time_list(self):
        return [f["time"] for f in self._vtms_dict["files"]]

    def files(self):
        return self._vtm_files