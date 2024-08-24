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

// Define module methods
static PyMethodDef PKIndicatorsMethods[] = {
    {"calculate_zigzag", (PyCFunction)calculate_zigzag, METH_VARARGS | METH_KEYWORDS, "Calculate ZigZag indicator with high/low markers and turning points"},
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
