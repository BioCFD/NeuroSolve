import os
import pyvista as pv
import numpy as np
from bioCFD.GeoTools.STLtools import find_neighbor_faces
from bioCFD.tools import find_replace


class NeuroSTL():

    def __init__(self, file_name, n_patches=4, feature_angle=45.0):
        self._file_name = file_name
        self._stl_mesh = self._read()
        self._npatches = n_patches
        self._splitted = False
        self._feature_angle = feature_angle
        self._split()
    
    def _read(self):
        """
        Get surface
        """
        return pv.read(self._file_name).extract_surface()

    def _split(self):
        stl_mesh = self._stl_mesh.compute_normals(
            cell_normals=True,
            # point_normals=True,
            split_vertices=True,
            # flip_normals=False,
            consistent_normals=True,
            auto_orient_normals=True,
            non_manifold_traversal=False,
            feature_angle=self._feature_angle,
            inplace=False
            )

        self._cc  = stl_mesh.connectivity()


    def get_region_id(self):

        regionIDs = np.unique(self._cc['RegionId'])
        return regionIDs

    def sizes(self):
        
        regionID_field = self._cc['RegionId']
        regionIDs = self.get_region_id()

        sizes = [regionID_field[regionID_field == i].shape[0] for i in regionIDs]
        sizes = np.array(sizes, dtype=int)
        return sizes

    def size_order(self):

        return self.sizes().argsort()

    def main_regions(self):

        main_regions = self.get_region_id()[self.size_order()][-self._npatches:]
        return main_regions

    def sad_regions(self):

        sad_regions = self.get_region_id()[self.size_order()][:-self._npatches]
        return sad_regions


    def sad_faces(self):

        cc = self._cc
        sad_regions = self.sad_regions()
        sad_faces = [list(cc["vtkOriginalCellIds"][cc['RegionId']==i]) for i in sad_regions]
        sad_faces = [item for sublist in sad_faces for item in sublist]
        return sad_faces        

    def collect_sad_faces(self, sad_faces):

        self._cc['RegionId'][sad_faces] = self._npatches

    def neighbor_cells(self, sad_faces):

        faces = self._stl_mesh.faces.reshape((-1,4))[:, 1:4]
        cell_neib = [find_neighbor_faces(faces, sad_face) for sad_face in sad_faces]
        return cell_neib

    def neighbor_regions_max(self, cell_neib):

        cell_neib_reg = [self._cc['RegionId'][i] for i in cell_neib]
        neib_count = [np.unique(i, return_counts=True) for i in cell_neib_reg]
    
        neib_reg_final = [(i[0]!=self._npatches).argmax(axis=0) for i in neib_count]

        return neib_reg_final
    
    def set_regions_max_neib(self):

        regionIDs = self.get_region_id()
        order = self.size_order()

        print(f"initial regions: {regionIDs[order]}")
        print(f"initial sizes: {self.sizes()[order]}")
        
        sad_faces = self.sad_faces()
        self.collect_sad_faces(sad_faces)
        regionIDs = self.get_region_id()

        print(f'After collection regions: {np.unique(regionIDs)}')
        print(f'Sad faces: {sad_faces}')

        cell_neib = self.neighbor_cells(sad_faces)
        neib_reg_final = self.neighbor_regions_max(cell_neib)
        self._cc['RegionId'][sad_faces] = neib_reg_final
        self._splitted = True


    def patches(self):
        
        main_regions = self.main_regions()
        patches_names = [f"outlet{i}" for i in range(1, self._npatches-1)]
        patches_names.append("inlet")
        patches_names.append("wall")
        patches = dict(zip(patches_names, main_regions))
        return patches

    def split(self):

        if not self._splitted:
            self.set_regions_max_neib()
        
        patches = self.patches()
        out = {}
        for pname, value in patches.items():
            self._cc.set_active_scalars('RegionId')
            threshed = self._cc.threshold([value, value]).extract_surface()
            out[pname] = threshed

        return out

    def areas(self):

        out = self.split()
        areas = {}
        for pname, sur in out.items():
            areas[pname] = sur.area
        return areas

    def write(self):

        out = self.split()
        for pname, sur in out.items():

            out_file = f"{pname}.stl"
            sur.save(out_file)
            find_replace(
                out_file,
                "solid Visualization Toolkit generated SLA File",
                f"solid {pname}")

    def patch_diameter(self, patch):

        area = self.areas()[patch]
        d = np.sqrt(area*4.0/np.pi)
        return d
