import numpy as np
from stl import mesh
import pyvista as pv

class STLReader():
    '''STLReader()
    helper class which reads stl file and gives the bounding box

    Notes
    -----
    A lot of work can be done here
    '''
    
    def __init__(self, file_name):
        self._file_name = file_name
        self._names = []
        self._min = []
        self._max = []
        
        for s in mesh.Mesh.from_multi_file(self._file_name):
            self._names.append(s.name.decode("utf-8"))
            self._min.append(s.min_)
            self._max.append(s.max_)
            self._mesh = s
    
    def names(self):
        return self._names
    
    def bounding_box(self):
        min_pt = np.array(self._min).min(axis=0)
        max_pt = np.array(self._max).max(axis=0)

        return min_pt, max_pt
    
    def mesh(self):
        return self._mesh


def find_faces_with_node(faces, index):
    """Pass the index of the node in question.
    Returns the face indices of the faces with that node."""
    return [i for i, face in enumerate(faces) if index in face]


def find_neighbor_faces(faces, index):
    """Pass the face index. 
    Returns the indices of all neighboring faces"""
    face = faces[index]
    sharing = set()
    for vid in face:
        [sharing.add(f) for f in find_faces_with_node(faces, vid)]
    sharing.remove(index)
    return list(sharing)

def find_neighbor_faces_by_edge(faces, index):
    """Pass the face index. 
    Returns the indices of all neighboring faces with shared edges."""
    face = faces[index]
    a = set(f for f in find_faces_with_node(faces, face[0]))
    a.remove(index)
    b = set(f for f in find_faces_with_node(faces, face[1]))
    b.remove(index)
    c = set(f for f in find_faces_with_node(faces, face[2]))
    c.remove(index)

    return [list(a.intersection(b)), list(b.intersection(c)), 
            list(a.intersection(c))]

