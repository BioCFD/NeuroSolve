import os
import json
import shutil
import argparse

from bioCFD.Cases.NeuroCase import NeuroCase
from bioCFD.tools import pack_case

'''
Small app which creates on case object and excute it
'''

def main():
    parser = argparse.ArgumentParser(
        description="Small app to prepare and run internal flow using OF-v2006")

    parser.add_argument("inparm", help="parameters input file in json format")
    parser.add_argument("--meshOnly", help="Init case and run mesh only", action="store_true")
    parser.add_argument("--solverOnly", help="Update BC and run solver only", action="store_true")
    parser.add_argument("--compress", help="Compress the case when finished or fails", action="store_true")

    args = parser.parse_args()
    inparm = args.inparm

    print(f'\tReading file: {inparm}\n')
    with open(inparm, 'r') as inp:
        parm_dict = json.load(inp)

    print(f'\tUser input parameters \n {json.dumps(parm_dict, indent=4)}\n')

    state_file = os.path.join(os.getcwd(), 'state.json')
    print(f'\tCheck case stats file: {state_file}\n')
    if os.path.isfile(state_file):
        print(f'state file found {state_file}\n')
        with open(state_file, 'r') as st:
            state_dict = json.load(st)
        
        print(f'\tCase state \n {json.dumps(state_dict, indent=4)}\n')

    else:
        print(f'\tNo state file found\n')
        state_dict = None

    case = NeuroCase(os.getcwd(), parm_dict, state_dict = state_dict)

    #try:
    case.initialise()
    case.correct()
    case.generate_mesh()
    case.run()
    if args.compress:
        pack_case(os.getcwd(), clean=True)
    #except:
    #    if args.compress:
    #        pack_case(os.getcwd(), clean=True)

    # if args.meshOnly:
    #     case.initialise()
        # case.correct()
    #     case.generate_mesh()
    # elif args.solverOnly:
    #     case.run()

if __name__ == "__main__":

    main()
