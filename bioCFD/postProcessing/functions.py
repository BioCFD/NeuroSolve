import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys


class MinMaxReader():

    def __init__(self, file_name):
        self._file = file_name
        self._data = self._read()
    
    def _read(self):
        with open(self._file, 'r') as infile:
            lines = infile.readlines()
        
        # ignore first line
        lines = lines[1:]
        # get header
        header = lines[0][1:].strip().split()
        
        # if 'patch' in header:
        #     header.remove('patch')
        print(header)

        data = [i.replace("(","").replace(")","").strip().split() for i in lines[1:]]

        nd = len(data[0])

        nh = len(header)

        if nh == nd:
            print("scalarField")

            df = pd.DataFrame(data, columns=header)
            df.set_index("Time", inplace=True)
            return df
        elif (nh - 2) * 3 + 2 == nd:
            print("vectorField")
            new_header = [i for i in header]
            df = pd.DataFrame(data, columns=header)
            df.set_index("Time", inplace=True)
        else:
            print("Not scalar nor vector")
            sys.exit()
        
    