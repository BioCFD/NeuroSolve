import os
import sys
import shutil
import numpy as np
from string import Template
from abc import ABC, abstractmethod

from bioCFD.GeoTools.NeuroSTL import NeuroSTL
from bioCFD.tools import dict_to_OF, update_OFdict, run_system, find_replace
from bioCFD.templates import *


class Mesh(ABC):
    '''Mesh()
        Abstract base class for meshing which defines the interface and implements
        runTime selector
    '''

    def __init__(self, case):
        '''
        Parameters
        ----------
        case : case
            case object
        '''
        self._case = case
        self._meshed = False

    @classmethod
    def select(cls, case):
        '''
        create a mesh object from mesh type name and case

        Parameter
        ---------
        name : str
            sub-type name
        case : case
            case object
        
        Returns
        -------
        mesh : name
        '''
        name = case.case_dict()['mesh']['type']
        subtype = [st for st in cls.__subclasses__() if st.__name__ == name]
        if len(subtype) == 0:
            names = [st.__name__ for st in cls.__subclasses__()]
            print(f'\t\n Type {name} not found, select one of {names}')
            sys.exit(1)

        return subtype[0](case)

    def logfile(self):
        '''
        Returns
        -------
        log_file_name : str
            log file name as log.<mesherTypeName>
        '''
        return f'log.{self.__class__.__name__}'

    def case(self):
        '''
        Returns
        -------
        case : case
            the case attached to the mesh
        '''
        return self._case

    def dict(self):
        return self.case().case_dict()['mesh']

    @abstractmethod
    def prepare(self):
        '''
        abstract method for prepration steps
        '''
        pass

    @abstractmethod
    def generate(self):
        '''
        abstract method for mesh generation
        '''
        self._meshed = True

    def meshed(self):
        return self._meshed

class cfMesh(Mesh):
    '''cfmesh(Mesh)
        Create mesh using msheDict of OpenFOAM. 
    '''

    def __init__(self, case):
        
        super().__init__(case)

    def _stl(self):
        '''
        Returns
        -------
        stl_file : str
            the stl file name
        '''

        geo_dict = self.case().case_dict()["geometry"]
        stl_file = geo_dict["all"]
        return stl_file

    def _prepare_stl(self):
        '''
        prepare the stl file, get patches etc...

        '''

        stl_file = os.path.join(self.case().path(), self._stl())
        if 'n_patches' in self.case().case_dict()["geometry"]:
            n_patches = self.case().case_dict()["geometry"]['n_patches']
        else:
            n_patches = 4
        if 'feature_angle' in self.case().case_dict()["geometry"]:
            feature_angle = self.case().case_dict()["geometry"]['feature_angle']
        else:
            feature_angle = 45

        geo = NeuroSTL(stl_file, n_patches=n_patches, feature_angle=feature_angle)

        print('Writing stl as patches')
        geo.write()

        return geo

    def _meshDict(self):

        return os.path.join(self.case().path(), "system", "meshDict")

    def _feature_extract(self):
        '''
        Prepare the needed files and extract the edges of the walls stl
        get fms

        Notes
        -----
        May be other stl files should be included
        '''
 
        
        name = os.path.splitext(
            os.path.join(self.case().path(), f'final_{self._stl()}'))[0]
        
        print('\tRunning surfaceFeatureEdges\n')
        _ = run_system(
            f"surfaceFeatureEdges {name}.stl {name}.fms  > log.surfaceFeatureEdges",
            cwd=self.case().path())



    def _clean(self):
        '''
        Remove all unnecessary entries in meshDict

        '''
        # src = os.path.join(self.case().path(), "system", "meshDict_fine")
        # dst = os.path.join(self.case().path(), "system", "meshDict")
        # shutil.copy2(src, dst)
        pass
        

    def _update_dict(self):
        '''
        clean and update subdicts
        '''
        geo = self._prepare_stl()
        self._clean()
        patches = geo.patches()
        name_stl = f'final_{self._stl()}'
        stl_file = os.path.join(self.case().path(), name_stl)
        # combine stls
        with open(stl_file,'w') as out:
            for pname, _ in patches.items():
                p_file = os.path.join(self.case().path(), f'{pname}.stl')
                with open(p_file,'r') as pstl:
                    out.write(pstl.read())
            

        mesh_dict = self._meshDict()
        stlname= os.path.splitext(name_stl)[0]
        update_OFdict(mesh_dict, 'surfaceFile', f' \" {stlname}.fms \" ')

        stl_mesh = geo
        print(f'Inlet diameter {stl_mesh.patch_diameter("inlet")}')
        print(f'Outlet_1 diameter {stl_mesh.patch_diameter("outlet1")}')
        print(f'Outlet_2 diameter {stl_mesh.patch_diameter("outlet2")}')
        all_area = stl_mesh.areas()
        smallest_Dim = min(all_area, key=lambda k: all_area[k])
        print('Smallest Dim : ' , smallest_Dim, ' ' , stl_mesh.patch_diameter(smallest_Dim))
        ##update dict
        n_minCellSize = self.dict()["n_minCellSize"]
        n_maxCellSize = self.dict()["n_maxCellSize"]
        update_OFdict(mesh_dict, 'minCellSize',
            f'{float(stl_mesh.patch_diameter(smallest_Dim)) /n_minCellSize}')
        update_OFdict(mesh_dict, 'maxCellSize',
            f'{float(stl_mesh.patch_diameter(smallest_Dim)) /n_maxCellSize}')  

    def prepare(self):
        '''
        cartesianMesh needs 
        '''
        
        self._update_dict()
        self._feature_extract()


    def generate(self):
        '''
        run cartesianMesh
        '''
        if not self._meshed:
            self.prepare()
            print('\tRunning cartesianMesh\n')
            _ = run_system(
                f"cartesianMesh  | tee {self.logfile()}",
                cwd=self.case().path())

            ### If condtion to look at the check mesh output 
            ### and to stop the process if negtive volume is found 
            print('\tRunning Improve Mesh Quality\n')
            _ = run_system(
                f"improveMeshQuality -nIterations 5 -nLoops 5 -nSurfaceIterations 5 | tee log.improveMeshQuality",
                cwd=self.case().path())        

            print('\tRunning Model scalling\n')
            _ = run_system(
                f"scaleMesh 0.001",
                cwd=self.case().path())  


            print('\tRunning checkMesh\n')
            _ = run_system(
                f"checkMesh -writeAllFields | tee log.checkMesh",
                cwd=self.case().path())

            _ = run_system(
                f"touch case.foam",
                cwd=self.case().path())  

            super().generate()
