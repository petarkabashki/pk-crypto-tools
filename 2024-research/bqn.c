#include <Python.h>
#include <stdlib.h>
#include <stdio.h>
#include <bqnffi.h>
#include <numpy/arrayobject.h>

// Define the eval function that will evaluate BQN code
static PyObject* pybqn_call(PyObject* self, PyObject* args) {
    const char* input_string;
    PyObject* numpy_array = NULL;

    // Print start of function
    printf("Starting pybqn_call...\n");

    // Parse the input tuple: expecting a BQN code string and an optional NumPy array or None
    if (!PyArg_ParseTuple(args, "s|O", &input_string, &numpy_array)) {
        printf("Failed to parse arguments.\n");
        return NULL;
    }

    // Debug print to confirm parsing
    printf("Parsed input_string: %s\n", input_string);

    BQNV bqn_arr = 0;  // Default to no array input

    bqn_init();      // Initialize BQN
    import_array();  // Initialize numpy C-API
    return PyModule_Create(&bqnmodule);
}

    // If a NumPy array is provided, convert it to a BQN array
    if (numpy_array && PyArray_Check(numpy_array)) {
        PyArrayObject* np_arr = (PyArrayObject*) numpy_array;
        int rank = PyArray_NDIM(np_arr);
        npy_intp* shape = PyArray_SHAPE(np_arr);
        int array_type = PyArray_TYPE(np_arr);
        void* array_data = PyArray_DATA(np_arr);

        // Convert NumPy array to BQN array
        switch (array_type) {
            case NPY_FLOAT:
            case NPY_DOUBLE:
                bqn_arr = bqn_makeF64Arr(rank, shape, array_data);
                break;
            case NPY_INT:
            case NPY_LONG:
                bqn_arr = bqn_makeI32Arr(rank, shape, array_data);
                break;
            default:
                PyErr_SetString(PyExc_TypeError, "Unsupported NumPy array type.");
                return NULL;
        }
    }

    // Evaluate the BQN expression
    BQNV result;
    if (bqn_arr) {
        printf("Evaluating BQN expression with NumPy array.\n");
        result = bqn_call1(bqn_evalCStr(input_string), bqn_arr);  // Use array input
        bqn_free(bqn_arr);  // Free the BQN array after use
    } else {
        printf("Evaluating BQN expression without NumPy array.\n");
        result = bqn_evalCStr(input_string);  // No array input
    }

    // Check if the evaluation succeeded
    if (result == 0) {
        printf("Evaluation failed: result is NULL.\n");
        PyErr_SetString(PyExc_RuntimeError, "Failed to evaluate BQN expression.");
        return NULL;
    }

    printf("BQN evaluation succeeded.\n");

    // Handle scalar results (BQN type 1 is scalar)
    int result_type = bqn_type(result);
    printf("BQN result type: %d\n", result_type);

    if (result_type == 1) {
        double scalar_value = bqn_toF64(result);
        bqn_free(result);  // Free the scalar BQN result
        printf("Returning scalar value: %f\n", scalar_value);
        return PyFloat_FromDouble(scalar_value);  // Return the scalar as a Python float
    }

    // Handle array results
    if (result_type == 0) {
        printf("Result is an array.\n");
        size_t result_rank = bqn_rank(result);
        npy_intp result_shape[result_rank];
        bqn_shape(result, result_shape);

        // Determine the type of the BQN array
        BQNElType eltype = bqn_directArrType(result);
        printf("BQN Element Type: %d\n", eltype);

        PyObject* numpy_array_res = NULL;
        if (eltype == elt_f64) {
            // Handle float64 arrays
            printf("Handling float64 array result.\n");
            numpy_array_res = PyArray_SimpleNew(result_rank, result_shape, NPY_FLOAT64);
            double* array_data_res = (double*)PyArray_DATA((PyArrayObject*)numpy_array_res);
            const double* bqn_data = bqn_directF64(result);
            memcpy(array_data_res, bqn_data, bqn_bound(result) * sizeof(double));
        } else if (eltype == elt_i32) {
            // Handle int32 arrays
            printf("Handling int32 array result.\n");
            numpy_array_res = PyArray_SimpleNew(result_rank, result_shape, NPY_INT32);
            int* array_data_res = (int*)PyArray_DATA((PyArrayObject*)numpy_array_res);
            const int32_t* bqn_data = bqn_directI32(result);
            memcpy(array_data_res, bqn_data, bqn_bound(result) * sizeof(int32_t));
        } else {
            PyErr_SetString(PyExc_TypeError, "Unsupported BQN array element type.");
            printf("Unsupported BQN array element type.\n");
            bqn_free(result);
            return NULL;
        }

        bqn_free(result);  // Free the BQN result after use
        printf("Returning NumPy array result.\n");
        return numpy_array_res;
    }

    // If result type is unsupported, return an error
    printf("Unsupported BQN result type.\n");
    bqn_free(result);
    PyErr_SetString(PyExc_TypeError, "Unsupported BQN result type.");
    return NULL;
}

// Define the Python module
static PyMethodDef BqnMethods[] = {
    {"call", pybqn_call, METH_VARARGS, "Evaluate BQN code and return the result as a scalar or array"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef bqnmodule = {
    PyModuleDef_HEAD_INIT,
    "bqn",               // Module name
    NULL,                // Module documentation
    -1,                  // Size of per-interpreter state of the module
    BqnMethods
};

// Initialize the module
PyMODINIT_FUNC PyInit_bqn(void) {
    printf("Initializing BQN module...\n");
    bqn_init();      // Initialize BQN
    import_array();  // Initialize numpy C-API
    return PyModule_Create(&bqnmodule);
}
