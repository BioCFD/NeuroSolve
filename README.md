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

# Copyright Terms and Conditions

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to use, copy, modify, merge, publish, distribute, sublicense, and permit persons to whom the Software is furnished to do the same, subject to the following conditions:
1.	The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
2.	The Software is licensed for non-commercial use only. "Non-commercial use" means use solely for research, educational, private or personal purposes, excluding purposes intended to generate monetary profit, compensation or any other commercial gain.
3.	Commercial use of the Software requires explicit prior permission from the copyright holder. Requests for commercial use licenses may be directed to ceo@bio-cfd.co.
4.	Modifications to the original Software must be clearly indicated, and strongly recommended to done as forks on Github, and the original copyright notice shall not be removed from any copies or substantial portions of the Software.
All users must accept these conditions to use this software and its documentation.

