#include <Python.h>
#include <numpy/arrayobject.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

double round_down(double value, int decimal_places) {
    double factor = pow(10.0, decimal_places);
    return floor(value * factor) / factor;
}


// C function to calculate trades (entry, exit indices)
static PyObject* enumerate_trades(PyObject* self, PyObject* args) {
    PyArrayObject *entry_mask, *exit_mask;
    int length, skip_first;

    // Parse Python arguments (two arrays and an integer)
    if (!PyArg_ParseTuple(args, "O!O!i",
                          &PyArray_Type, &entry_mask,
                          &PyArray_Type, &exit_mask,
                          &skip_first))
        return NULL;

    // Ensure input arrays are of the same length
    length = (int)PyArray_DIM(entry_mask, 0);
    if (length != PyArray_DIM(exit_mask, 0)) {
        PyErr_SetString(PyExc_ValueError, "All input arrays must have the same length");
        return NULL;
    }

    // Ensure skip_first is within valid range
    if (skip_first >= length || skip_first < 0) {
        PyErr_SetString(PyExc_ValueError, "skip_first must be a non-negative integer less than the length of the arrays");
        return NULL;
    }

    // Initialize pointers for the input arrays
    long *entry_data = (long *)PyArray_DATA(entry_mask);
    long *exit_data = (long *)PyArray_DATA(exit_mask);

    // Dynamic arrays to hold entry and exit indices as Python lists
    PyObject *entry_list = PyList_New(0);
    PyObject *exit_list = PyList_New(0);

    int current_position = 0;

    // Loop through the array to calculate positions and trade details
    for (int i = skip_first; i < length; i++) {
        if (current_position == 1 && exit_data[i] == 1) {
            // Close the position
            PyList_Append(exit_list, PyLong_FromLong(i));
            current_position = 0;
        } else if (current_position == 0 && entry_data[i] == 1) {
            // Open a new position
            PyList_Append(entry_list, PyLong_FromLong(i));
            current_position = 1;
        }
    }

    // If we have more entries than exits, assume the last data point is the exit
    if (PyList_Size(entry_list) > PyList_Size(exit_list)) {
        PyList_Append(exit_list, PyLong_FromLong(length - 1));
    }

    // Return the trade entries and exits as Python lists
    return Py_BuildValue("OO", entry_list, exit_list);
}


// Define the methods for the module
static PyMethodDef PositionToolsMethods[] = {
    {"enumerate_trades", enumerate_trades, METH_VARARGS, "Calculate trades (entry index, exit index, and position type) from entry/exit masks"},
 
    {NULL, NULL, 0, NULL}
};

// Define the module
static struct PyModuleDef positiontoolsmodule = {
    PyModuleDef_HEAD_INIT,
    "position_tools",
    NULL,
    -1,
    PositionToolsMethods
};

// Initialize the module
PyMODINIT_FUNC PyInit_position_tools(void) {
    import_array();  // Initialize numpy C-API
    return PyModule_Create(&positiontoolsmodule);
}


// f'gcc -shared -o positions.so -fPIC positions.c -I{sysconfig.get_path("include")} -I{np.get_include()}'

// clear & rm position_tools.so & gcc -shared -o position_tools.so -fPIC position_tools.c -I/home/mu6mula/miniconda3/envs/py310/include/python3.10 -I/home/mu6mula/miniconda3/envs/py310/lib/python3.10/site-packages/numpy/core/include