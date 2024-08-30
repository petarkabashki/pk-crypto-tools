#include <Python.h>
#include <numpy/arrayobject.h>

// Function to calculate ZigZag indicator and return high/low markers and turning points
static PyObject* calculate_zigzag(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyArrayObject *price_array;
    double epsilon = 0.5;  // Default epsilon

    static char *kwlist[] = {"prices", "epsilon", NULL};

    // Parse Python arguments with keywords
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!|d", kwlist, &PyArray_Type, &price_array, &epsilon)) {
        return NULL;
    }

    // Ensure the input is a 1D numpy array
    if (PyArray_NDIM(price_array) != 1) {
        PyErr_SetString(PyExc_ValueError, "Price array must be a 1D numpy array.");
        return NULL;
    }

    // Get the length of the array
    npy_intp length = PyArray_DIM(price_array, 0);

    // Create output arrays for high/low markers and turning points
    PyObject *high_low_markers = PyArray_SimpleNew(1, &length, NPY_INT);
    PyObject *turning_points = PyArray_SimpleNew(1, &length, NPY_INT);

    int *markers_data = (int*)PyArray_DATA((PyArrayObject*)high_low_markers);
    int *turning_points_data = (int*)PyArray_DATA((PyArrayObject*)turning_points);
    double *price_data = (double*)PyArray_DATA(price_array);

    int direction = 0;
    int last_extreme_index = 0;
    double last_extreme_value = price_data[0];

    // Initialize output arrays
    for (npy_intp i = 0; i < length; i++) {
        markers_data[i] = 0;
        turning_points_data[i] = 0;
    }

    // Process each price point
    for (npy_intp i = 1; i < length; i++) {
        double current_price = price_data[i];
        double price_diff = current_price - last_extreme_value;

        if (direction == 0) {
            if (fabs(price_diff) >= epsilon) {
                direction = (price_diff > 0) ? 1 : -1;
                last_extreme_index = i;
                last_extreme_value = current_price;
                markers_data[i] = (direction == 1) ? 1 : -1;
                turning_points_data[i] = direction;
            }
        } else if (direction == 1) {
            if (current_price >= last_extreme_value) {
                last_extreme_index = i;
                last_extreme_value = current_price;
            } else if (last_extreme_value - current_price >= epsilon) {
                direction = -1;
                markers_data[last_extreme_index] = 1;
                turning_points_data[last_extreme_index] = 1;

                last_extreme_index = i;
                last_extreme_value = current_price;
                // markers_data[i] = -1;
                turning_points_data[i] = -1;
            }
        } else if (direction == -1) {
            if (current_price <= last_extreme_value) {
                last_extreme_index = i;
                last_extreme_value = current_price;
            } else if (current_price - last_extreme_value >= epsilon) {
                direction = 1;
                markers_data[last_extreme_index] = -1;
                turning_points_data[last_extreme_index] = -1;

                last_extreme_index = i;
                last_extreme_value = current_price;
                // markers_data[i] = 1;
                turning_points_data[i] = 1;
            }
        }
    }

    markers_data[last_extreme_index] = (direction == 1) ? 1 : -1;
    turning_points_data[last_extreme_index] = direction;

    return Py_BuildValue("OO", high_low_markers, turning_points);
}

static PyObject* find_cross(PyObject* self, PyObject* args) {
    PyArrayObject *fast_array, *slow_array;
    int direction;

    // Parse the input arguments
    if (!PyArg_ParseTuple(args, "O!O!i",
                          &PyArray_Type, &fast_array,
                          &PyArray_Type, &slow_array,
                          &direction)) {
        return NULL;
    }

    // Check that the arrays have the same length
    npy_intp length = PyArray_DIM(fast_array, 0);
    if (length != PyArray_DIM(slow_array, 0)) {
        PyErr_SetString(PyExc_ValueError, "Input arrays must have the same length.");
        return NULL;
    }

    // Get pointers to the data in the NumPy arrays
    double *fast_data = (double*)PyArray_DATA(fast_array);
    double *slow_data = (double*)PyArray_DATA(slow_array);

    // Create an output array of the same length
    npy_intp dims[1] = {length};
    PyObject *result = PyArray_SimpleNew(1, dims, NPY_INT);
    int *result_data = (int*)PyArray_DATA(result);

    // Initialize the result array to zeros
    for (npy_intp i = 0; i < length; i++) {
        result_data[i] = 0;
    }

    // Calculate the crossings
    for (npy_intp i = 1; i < length; i++) {
        if (direction == 1) {
            // Upward crossing: fast crosses above slow
            if (fast_data[i-1] <= slow_data[i-1] && fast_data[i] > slow_data[i]) {
                result_data[i] = 1;
            }
        } else if (direction == -1) {
            // Downward crossing: fast crosses below slow
            if (fast_data[i-1] >= slow_data[i-1] && fast_data[i] < slow_data[i]) {
                result_data[i] = -1;
            }
        } else {
            PyErr_SetString(PyExc_ValueError, "Direction must be 1 (upwards) or -1 (downwards).");
            return NULL;
        }
    }

    // Return the result array
    return Py_BuildValue("O", result);
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

// Define module methods
static PyMethodDef PKIndicatorsMethods[] = {
    {"calculate_zigzag", (PyCFunction)calculate_zigzag, METH_VARARGS | METH_KEYWORDS, "Calculate ZigZag indicator with high/low markers and turning points"},
    {"find_cross", find_cross, METH_VARARGS, "Find crossovers between two arrays."},
    {"count_since_last_signal", count_since_last_signal, METH_VARARGS, "Count elements since last signal."},
    {NULL, NULL, 0, NULL}
};

// Define the module
static struct PyModuleDef pkindicatorsmodule = {
    PyModuleDef_HEAD_INIT,
    "pkindicators",
    NULL,
    -1,
    PKIndicatorsMethods
};

// Initialize the module
PyMODINIT_FUNC PyInit_pkindicators(void) {
    import_array();
    return PyModule_Create(&pkindicatorsmodule);
}

/*
import sysconfig
cmodule = 'pkindicators'
f'clear & rm {cmodule}.so & gcc -shared -o {cmodule}.so -fPIC {cmodule}.c -I{sysconfig.get_path("include")} -I{np.get_include()}'
 */