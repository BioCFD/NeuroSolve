import os
import json
import shutil
import argparse

from bioCFD.Cases.NeuroCase import NeuroCase
from bioCFD.tools import pack_case
from bioCFD.postProcessing.vtms import VTM, VTMS

'''
Small app which creates on case object and excute it
'''

def main():
    parser = argparse.ArgumentParser(
        description="Small app for postProcessing")

    # parser.add_argument("inparm", help="parameters input file in json format")
    # parser.add_argument("--meshOnly", help="Init case and run mesh only", action="store_true")
    # parser.add_argument("--solverOnly", help="Update BC and run solver only", action="store_true")
    # parser.add_argument("--compress", help="Compress the case when finished or fails", action="store_true")

    args = parser.parse_args()
    # inparm = args.inparm

    # posted = ["wallShearStress1", "yPlus1"]
    # data_folders = [ os.path.join("postProcessing", i) for i in posted]
    # latest_time = [os.listdir(i)[-1] for i in data_folders]

    # data_files = [os.path.join(df,t,p[:-1])+".dat" for df,t,p in zip(data_folders,latest_time, posted)]
    # indata = [MinMaxReader(i) for i in data_files]

    import pyvista as pv
    import numpy as np
    import pandas as pd

    def get_kres(internal_data):
        up2mean = internal_data['UPrime2Mean']
        return 0.5 * (up2mean[:,0] + up2mean[:,1] +up2mean[:,2])

    def mag(vec):
        return np.linalg.norm(vec, axis=1)

    def get_ti(internal_data):
        k_res = get_kres(internal_data)
        k_mod = internal_data['turbulenceProperties:k']

        Umean = mag(internal_data['U'])
        ktot = k_res+k_mod
        ti = np.sqrt((2/3.0) * (k_res+k_mod))/Umean
        
        return ti

    case_name = os.path.basename(os.getcwd())
    file_name = os.path.join("VTK",f"{case_name}.vtm.series")
    vtms = VTMS(file_name)
    data = {}
    data['kres'] = []
    data['time'] = []
    data['WSS'] = []
    data['p'] = []
    data['nu_near'] = []
    data['TI_near'] = []
    data['TI'] = []
    count = 0


    for f in vtms.files():

        if f.split("_")[-1] == "00000.vtm":
            print('Ignore zero time step {f}')
            continue
        print(f"{count+1}/{len(vtms.files())}")
        vtm = VTM(f)

        if count == 0:

            # estimate volume
            sized = vtm.internal().compute_cell_sizes()
            cell_volumes = sized.cell_arrays["Volume"]
            volume = vtm.internal().volume
            w = cell_volumes

            # estimate area
            areaded = vtm.boundary()['wall'].compute_cell_sizes()
            face_areas = areaded.cell_arrays["Area"]
            area = vtm.boundary()['wall'].area
            fw = face_areas





        data['time'].append(vtm.time())
        data['kres'].append(np.average(get_kres(vtm.internal()), weights=w))
        data['TI'].append(np.average(get_ti(vtm.internal()), weights=w))

        data['WSS'].append(
            np.average(
                mag(vtm.boundary()['wall']['wallShearStress']), weights=fw))
        data['p'].append(
            np.average(
                vtm.boundary()['wall']['p'], weights=fw))
        

        # apply Threshold

        threshed = vtm.internal().compute_cell_sizes().threshold(
            value=[0.0, 0.0002],scalars='wallDistance')
        tw = threshed.cell_arrays["Volume"]

        data['nu_near'].append(
            np.average(
                threshed.cell_arrays['nu'], weights=tw))
        data['TI_near'].append(
            np.average(
                get_ti(threshed), weights=tw))

        # threshed.save('threshed.vtk')

        count +=1

    
    df = pd.DataFrame(data)
    df.set_index('time', inplace=True)
    # print(df)
    df.to_csv('data.csv')

    

if __name__ == "__main__":

    main()
