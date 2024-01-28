
import subprocess
import shutil
import fileinput
import os
import tarfile


def run_system(command, cwd=None, *args, **kwargs):

    out = subprocess.run(
        command,
        shell=True, encoding='utf-8', check=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, cwd=cwd, *args, **kwargs)
    return out

def update_OFdict(OFdict, key, value):

    cs = f'foamDictionary {OFdict} -entry {key} -set {value} -disableFunctionEntries -precision 12'
    return run_system(cs)

def background_mesh(backgroundMeshDict, target_case):

    src = os.path.join(os.environ["BIOCFD_TEMP"], "blockMeshDict")
    dst = os.path.join(target_case, "system", "blockMeshDict")
    # if os.path.isfile(dst):
    #     os.remove(dst)
    shutil.copy(src, dst)
    return update_OFdict(dst, "backgroundMesh", f'"{backgroundMeshDict}"')

def dict_to_OF(dict):

    of = ""
    for key, value in dict.items():
        of += f"\t{key} {value};\n"
    return "{\n" + of + "}"


def find_replace(filename, old_str, new_str):
    '''
    find and replace string in a file
    '''
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            print(line.replace(old_str, new_str), end='')


def pack_case(case_path, clean=False):
    print(f'\n\tpacking case: {case_path}')
    files = os.listdir(case_path)

    case_name = os.path.basename(case_path)
    out_tar = os.path.join(case_path, f'{case_name}.tar.gz')
    print(f'\n\tWriting :{out_tar}')
    with tarfile.open(out_tar, "w:gz") as tar:
        _ = [tar.add(name) for name in files]

    tar.close()
    print('\n\t case packed')
    if clean:
        print('\n\t cleaning case files after compression')
        for f in files:
            if os.path.isfile(f):
                os.remove(f)
            elif os.path.isdir(f):
                shutil.rmtree(f)

        print('\n\t case cleaned')
        