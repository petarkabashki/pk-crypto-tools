#include <Python.h>
#include <numpy/arrayobject.h>

// Function to calculate ZigZag indicator and return high/low markers and turning points.
// Now accepts separate arrays for highs and lows.
static PyObject* calculate_zigzag(PyObject* self, PyObject* args, PyObject* kwargs) {
    PyArrayObject *highs_array = NULL, *lows_array = NULL;
    double epsilon = 0.5;  // Default epsilon

    static char *kwlist[] = {"highs", "lows", "epsilon", NULL};

    // Parse Python arguments with keywords
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O!O!|d", kwlist,
                                     &PyArray_Type, &highs_array,
                                     &PyArray_Type, &lows_array,
                                     &epsilon)) {
        return NULL;
    }

    // Ensure both arrays are 1D and of equal length
    if (PyArray_NDIM(highs_array) != 1 || PyArray_NDIM(lows_array) != 1) {
        PyErr_SetString(PyExc_ValueError, "Highs and lows arrays must be 1D.");
        return NULL;
    }
    npy_intp length_highs = PyArray_DIM(highs_array, 0);
    npy_intp length_lows = PyArray_DIM(lows_array, 0);
    if (length_highs != length_lows) {
        PyErr_SetString(PyExc_ValueError, "Highs and lows arrays must be of the same length.");
        return NULL;
    }
    npy_intp length = length_highs;

    // Create output arrays for high/low markers and turning points
    PyObject *high_low_markers = PyArray_SimpleNew(1, &length, NPY_INT);
    PyObject *turning_points = PyArray_SimpleNew(1, &length, NPY_INT);
    int *markers_data = (int*)PyArray_DATA((PyArrayObject*)high_low_markers);
    int *turning_points_data = (int*)PyArray_DATA((PyArrayObject*)turning_points);
    double *highs = (double*)PyArray_DATA(highs_array);
    double *lows = (double*)PyArray_DATA(lows_array);

    // Initialize the output arrays to 0.
    for (npy_intp i = 0; i < length; i++) {
        markers_data[i] = 0;
        turning_points_data[i] = 0;
    }

    int direction = 0;      //  1: uptrend, -1: downtrend, 0: not yet established
    int last_extreme_index = 0;
    double last_extreme_value = 0.0;
    // int current_extreme_index = 0;
    // double current_extreme_value = 0.0;

    // --- Pre-scan Phase: Determine the initial turning point after a significant move ---
    // We track candidate extremes from the start.
    int candidate_low_index = 0, candidate_high_index = 0;
    double candidate_low = lows[0];
    double candidate_high = highs[0];
    int trend_detected = 0;
    int i = 1;
    for (; i < length; i++) {
        // Update candidate for uptrend (lowest low)
        if (lows[i] < candidate_low) {
            candidate_low = lows[i];
            candidate_low_index = i;
        }
        // Update candidate for downtrend (highest high)
        if (highs[i] > candidate_high) {
            candidate_high = highs[i];
            candidate_high_index = i;
        }
        // Check if an upward move is detected:
        //    current high minus the lowest candidate low is at least epsilon.
        if (highs[i] / candidate_low -1 >= epsilon) {
            trend_detected = 1;
            direction = 1; // uptrend
            // current_extreme_index = i;
            // current_extreme_value = highs[i];
            // The initial turning point will be the lowest low candidate.
            last_extreme_index = candidate_low_index;
            last_extreme_value = candidate_low;
            // For an uptrend, mark the turning point as a trough (use -1).
            markers_data[last_extreme_index] = -1;
            turning_points_data[i] = 1;

            last_extreme_index = candidate_high_index;
            last_extreme_value = candidate_high;
            break;
        }
        // Check if a downward move is detected:
        //    highest candidate high minus current low is at least epsilon.
        if (candidate_high / lows[i] -1 >= epsilon) {
            trend_detected = -1;
            direction = -1; // downtrend
            // current_extreme_index = i;
            // current_extreme_value = lows[i];
            // The initial turning point will be the highest high candidate.
            last_extreme_index = candidate_high_index;
            last_extreme_value = candidate_high;
            // For a downtrend, mark the turning point as a peak (use 1).
            markers_data[last_extreme_index] = 1;
            turning_points_data[last_extreme_index] = -1;

            last_extreme_index = candidate_low_index;
            last_extreme_value = candidate_low;
            break;
        }
    }

    // If no significant move was detected in the pre-scan, return arrays of zeros.
    if (trend_detected == 0) {
        return Py_BuildValue("OO", high_low_markers, turning_points);
    }

    // --- Main Loop: Process remaining data starting from the next index ---
    for (i = i + 1; i < length; i++) {
        if (direction == 1) {  // Currently in an uptrend a high rises at least epsilon above the current low.
            // Check for reversal: if
            if (last_extreme_value / lows[i] -1 >= epsilon) {
                markers_data[last_extreme_index] = 1;
                turning_points_data[i] = -1;
                direction = -1;
                last_extreme_index = i;
                last_extreme_value = highs[last_extreme_index];
            }
            // In a downtrend, update the turning point if a new higher high is found.
            if (highs[i] > last_extreme_value) {
                last_extreme_index = i;
                last_extreme_value = highs[i];
            }
        } else if (direction == -1) {  // Currently in a downtrend
            // Check for reversal: if a low drops at least epsilon below the current high.
            if (highs[i] / last_extreme_value -1 >= epsilon) {
                // Finalize the current turning point.
                markers_data[last_extreme_index] = -1;
                turning_points_data[i] = 1;
                // Switch to a downtrend.
                direction = 1;
                last_extreme_index = i;
                last_extreme_value = lows[last_extreme_index];
            }
            // In an uptrend, update the turning point if a new lower low is found.
            if (lows[i] < last_extreme_value) {
                last_extreme_index = i;
                last_extreme_value = lows[i];
            }
        }
    }

    // Mark the final extreme point.
    if (direction == 1) {
        markers_data[last_extreme_index] = -1;
        turning_points_data[last_extreme_index] = -1;
    } else {
        markers_data[last_extreme_index] = 1;
        turning_points_data[last_extreme_index] = 1;
    }

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