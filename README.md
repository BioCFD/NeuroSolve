# NeuroCFD

- Install python3-venv (v3.7+) (once for each system)
    ```bash
    sudo apt-get install python3-venv

- Create a new virtual enviroment  (once for each system)
    ```bash
    python3 -m venv path/to/neuroCFDvenv

- Activate the venv
    ```bash
    source path/to/neuroCFDvenv/bin/activate

**The above steps if you want to work in python-venv but you can use the system version**

- Install all the required python pakages (once for each system)
    ```bash
    pip install -r requirements.txt

- Source OpenFOAM-v2012 as usual

- Source NeuroCFD
    ```bash
    source etc/bashrc
