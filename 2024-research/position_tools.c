#include <Python.h>
#include <numpy/arrayobject.h>

#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
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

static PyObject* calculate_positions(PyObject* self, PyObject* args) {
    PyObject* itrades_obj, *log_price_array;
    // int price_data_length;

    // Parse the input arguments: itrades array and the length of the price data array
    if (!PyArg_ParseTuple(args, "O!O!", 
            &PyArray_Type, &itrades_obj, 
            &PyArray_Type, &log_price_array
        )) {
        return NULL;
    }

    // Ensure itrades is indeed a NumPy array
    if (!PyArray_Check(itrades_obj)) {
        PyErr_SetString(PyExc_TypeError, "Expected a NumPy array for itrades");
        return NULL;
    }

    // Ensure itrades is indeed a NumPy array
    if (!PyArray_Check(log_price_array)) {
        PyErr_SetString(PyExc_TypeError, "Expected a NumPy array for log prices");
        return NULL;
    }

    // Get the shape of the itrades array
    npy_intp* itrades_shape = PyArray_SHAPE((PyArrayObject*)itrades_obj);
    npy_intp num_trades = itrades_shape[0];

    // Get pointers to the data of itrades
    int* itrades_data = (int*)PyArray_DATA((PyArrayObject*)itrades_obj);


    // Get the shape of the itrades array
    npy_intp* log_prices_shape = PyArray_SHAPE((PyArrayObject*)log_price_array);
    npy_intp num_log_prices = log_prices_shape[0];

    // Get pointers to the data of itrades
    double* log_prices_data = (double*)PyArray_DATA((PyArrayObject*)log_price_array);

    // Create an array of unrealized initialized to 0
    npy_intp dims[1] = {num_log_prices};
    PyObject* unrealized_array = PyArray_SimpleNew(1, dims, NPY_DOUBLE);

    if (unrealized_array == NULL) {
        PyErr_SetString(PyExc_TypeError, "Error creating the unrealized array.");
        return NULL;
    }
    double* unrealized_data = (double*)PyArray_DATA((PyArrayObject*)unrealized_array);

    // Initialize the unrealized array to 0
    for (int i = 0; i < num_log_prices; i++) {
        unrealized_data[i] = 0;
    }

    // Fill the unrealized array based on itrades
    double unrealized_total = 0;
    for (npy_intp i = 0; i < num_trades; i++) {
        int start_index = itrades_data[i * 3];
        int end_index = itrades_data[i * 3 + 1];
        int position_type = itrades_data[i * 3 + 2];
        
        // double start_trade_log_price = log_prices_data[start_index];
        // double start_pos_log_price = 0;
        unrealized_data[start_index] = unrealized_total;
        // unrealized_total -= (log_prices_data[start_index] * position_type);
        // Set positions from start_index to end_index with position_type
        for (int j = start_index + 1; j <= end_index - 1; j++) {
            unrealized_data[j] = unrealized_total + (( log_prices_data[j] - log_prices_data[start_index])* position_type) ;
        }
        unrealized_total += ((log_prices_data[end_index] - log_prices_data[start_index])* position_type);
        unrealized_data[end_index] = unrealized_total;
    }

    // fill unrealized between trades
    for (npy_intp i = 1; i < num_trades; i++) {
        int end_prev_index = itrades_data[(i-1) * 3 + 1];
        int start_index = itrades_data[i * 3];
        for (int j = end_prev_index+1; j <= start_index-1; j++) {
            unrealized_data[j] = unrealized_data[end_prev_index];
        }    
    }
    int end_last_trade_index = itrades_data[(num_trades-1) * 3 + 1];
    for (int j = end_last_trade_index + 1; j <= num_log_prices - 1; j++) {
        unrealized_data[j] = unrealized_data[end_last_trade_index];
    }  
    // Return the positions array
    return Py_BuildValue("O", unrealized_array);
}


static PyObject* count_since_last_signal(PyObject* self, PyObject* args) {
    PyObject *signal_array_obj;
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &signal_array_obj)) {
        return NULL;
    }

    PyArrayObject *signal_array = (PyArrayObject*) signal_array_obj;
    npy_intp n = PyArray_DIM(signal_array, 0);
    npy_bool *signals = (npy_bool*)PyArray_DATA(signal_array); // Use npy_bool for boolean array

    // Create a new NumPy array for the result
    PyArrayObject *result_array = (PyArrayObject*)PyArray_SimpleNew(1, PyArray_DIMS(signal_array), NPY_INT);
    int *result = (int*)PyArray_DATA(result_array);

    // Initialize the last_signal_index to -1 (no signal found yet)
    int last_signal_index = -1;

    for (npy_intp i = 0; i < n; ++i) {
        if (signals[i]) {  // If the signal is True
            last_signal_index = i;
        }
        if (last_signal_index == -1) {
            result[i] = -1;  // No signal found yet
        } else {
            result[i] = i - last_signal_index;
        }
    }
    return Py_BuildValue("O", result_array);
}

// Define the methods for the module
static PyMethodDef PositionToolsMethods[] = {
    {"calculate_trades", calculate_trades, METH_VARARGS, "Calculate trades (entry index, exit index, and position type) from entry/exit masks"},
    {"calculate_positions", calculate_positions, METH_VARARGS, "Calculate positions from itrades"},
    {"count_since_last_signal", count_since_last_signal, METH_VARARGS, "Count elements since last signal."},

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



// clear & rm position_tools.so & gcc -shared -o position_tools.so -fPIC position_tools.c -I/home/mu6mula/miniconda3/envs/py310/include/python3.10 -I/home/mu6mula/miniconda3/envs/py310/include/python3.10 -I/home/mu6mula/miniconda3/envs/py310/lib/python3.10/site-packages/numpy/core/include