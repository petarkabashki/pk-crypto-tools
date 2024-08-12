#include <Python.h>
#include <numpy/arrayobject.h>

// C function to calculate trades (entry, exit indices, and position type)
static PyObject* calculate_trades(PyObject* self, PyObject* args) {
    PyArrayObject *long_entry_mask, *long_exit_mask, *short_entry_mask, *short_exit_mask;
    int length;
    npy_intp dims[1];

    // Parse Python arguments (four arrays)
    if (!PyArg_ParseTuple(args, "O!O!O!O!",
                          &PyArray_Type, &long_entry_mask,
                          &PyArray_Type, &long_exit_mask,
                          &PyArray_Type, &short_entry_mask,
                          &PyArray_Type, &short_exit_mask))
        return NULL;

    // Ensure input arrays are of the same length
    length = (int)PyArray_DIM(long_entry_mask, 0);
    if (length != PyArray_DIM(long_exit_mask, 0) ||
        length != PyArray_DIM(short_entry_mask, 0) ||
        length != PyArray_DIM(short_exit_mask, 0)) {
        PyErr_SetString(PyExc_ValueError, "All input arrays must have the same length");
        return NULL;
    }

    // Create output array for positions
    dims[0] = length;
    PyObject *positions = PyArray_SimpleNew(1, dims, NPY_INT);
    int *pos = (int *)PyArray_DATA(positions);

    // Initialize the position state and trade details
    int current_position = 0;
    int entry_index = -1;
    int trade_count = 0;

    // Estimate maximum number of trades (this is a conservative estimate)
    int max_trades = length / 2;

    // Allocate array for trade details (entry index, exit index, and position type)
    npy_intp trade_dims[2] = {max_trades, 3};  // Three columns: entry_index, exit_index, position_type
    PyObject *trade_details = PyArray_SimpleNew(2, trade_dims, NPY_INT);
    int *trade_data = (int *)PyArray_DATA(trade_details);

    // Loop through the array to calculate positions and trade details
    for (int i = 0; i < length; i++) {
        // Handle closing of the current position
        if (current_position == 1 && (*((int *)PyArray_GETPTR1(short_entry_mask, i)) || *((int *)PyArray_GETPTR1(long_exit_mask, i)))) {
            // Close the long position
            trade_data[trade_count * 3] = entry_index;
            trade_data[trade_count * 3 + 1] = i;
            trade_data[trade_count * 3 + 2] = 1;
            trade_count++;
            current_position = 0;
            entry_index = -1;
        } else if (current_position == -1 && (*((int *)PyArray_GETPTR1(long_entry_mask, i)) || *((int *)PyArray_GETPTR1(short_exit_mask, i)))) {
            // Close the short position
            trade_data[trade_count * 3] = entry_index;
            trade_data[trade_count * 3 + 1] = i;
            trade_data[trade_count * 3 + 2] = -1;
            trade_count++;
            current_position = 0;
            entry_index = -1;
        }

        // Handle opening of a new position
        if (current_position == 0) {
            if (*((int *)PyArray_GETPTR1(long_entry_mask, i))) {
                // Open a long position
                current_position = 1;
                entry_index = i;
            } else if (*((int *)PyArray_GETPTR1(short_entry_mask, i))) {
                // Open a short position
                current_position = -1;
                entry_index = i;
            }
        }

        pos[i] = current_position;
    }

    // Resize the trade_details array to match the actual number of trades
    if (trade_count < max_trades) {
        npy_intp new_dims[2] = {trade_count, 3};
        PyObject *new_trade_details = PyArray_SimpleNew(2, new_dims, NPY_INT);
        int *new_trade_data = (int *)PyArray_DATA(new_trade_details);
        for (int j = 0; j < trade_count; j++) {
            new_trade_data[j * 3] = trade_data[j * 3];
            new_trade_data[j * 3 + 1] = trade_data[j * 3 + 1];
            new_trade_data[j * 3 + 2] = trade_data[j * 3 + 2];
        }
        Py_DECREF(trade_details);
        trade_details = new_trade_details;
    }

    // Return the trade details (entry index, exit index, and position type)
    return Py_BuildValue("O", trade_details);
}

// Define the methods for the module
static PyMethodDef PositionToolsMethods[] = {
    {"calculate_trades", calculate_trades, METH_VARARGS, "Calculate trades (entry index, exit index, and position type) from entry/exit masks"},
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



// gcc -shared -o position_tools.so -fPIC position_tools.c -I/home/mu6mula/miniconda3/envs/py310/include/python3.10 -I/home/mu6mula/miniconda3/envs/py310/include/python3.10 -I/home/mu6mula/miniconda3/envs/py310/lib/python3.10/site-packages/numpy/core/include