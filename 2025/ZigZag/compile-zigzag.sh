#!/bin/bash

# Compile the zigzag.c file into a Python C extension module (zigzag.so)
gcc -shared -fPIC $(python3-config --includes) -I$(python -c "import numpy as np; print(np.get_include())") zigzag.c -o zigzag.so -Wl,-export-dynamic -Wno-deprecated-declarations