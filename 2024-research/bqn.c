#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <bqnffi.h>
#include <numpy/arrayobject.h>

// Define the eval function that will evaluate BQN code
static PyObject* pybqn_call(PyObject* self, PyObject* args) {
    PyObject* numpy_array;
    const char* input_string;

    // Parse the input tuple: expecting a NumPy array and a string
    if (!PyArg_ParseTuple(args, "sO!", &input_string, &PyArray_Type, &numpy_array)) {
        return NULL;
    }

    // Ensure the input is indeed a NumPy array
    if (!PyArray_Check(numpy_array)) {
        return NULL;
    }

    // Get the rank (number of dimensions) of the array
    int rank = PyArray_NDIM((PyArrayObject*)numpy_array);
    // return PyFloat_FromDouble(rank);
    // printf('input rank: %i\n',rank);
    // Get the shape of the array (pointer to an array of npy_intp)
    npy_intp* shape = PyArray_SHAPE((PyArrayObject*)numpy_array);

    // return PyFloat_FromDouble(shape[0]);
    // Get the type of the NumPy array
    int array_type = PyArray_TYPE((PyArrayObject*)numpy_array);
    // printf('input shape: %i\n',shape[0]);
    // return shape;
    void* array_data = PyArray_DATA((PyArrayObject*)numpy_array);

    BQNV bqn_arr;
    rank = 1;
    switch (array_type)
    {
    case NPY_BOOL:
    case NPY_BYTE:
    case NPY_UBYTE:
        // bqn_arr = bqn_makeI8Arr(rank, shape, PyArray_DATA((PyArrayObject*)numpy_array));
        // /* code */
        // break;
    case NPY_SHORT:
    case NPY_USHORT:
        bqn_arr = bqn_makeI16Arr(rank, shape, array_data);
        /* code */
        break;
    case NPY_INT:
    case NPY_UINT:
    case NPY_LONG:
    case NPY_ULONG:
        bqn_arr = bqn_makeI32Arr(rank, shape, array_data);
        break;
    case NPY_LONGLONG:
    case NPY_ULONGLONG:
        bqn_arr = bqn_makeI32Arr(rank, shape, PyArray_DATA((PyArrayObject*)numpy_array));
        break;
    case NPY_FLOAT:
    case NPY_DOUBLE:
    case NPY_LONGDOUBLE:
    case NPY_CFLOAT:
    case NPY_CDOUBLE:
    case NPY_CLONGDOUBLE:
        bqn_arr = bqn_makeF64Arr(rank, shape, array_data);
        break;
    default:
        bqn_arr = bqn_makeF64Arr(rank, shape, array_data);
        break;
    }

    BQN_EXP BQNV xpr = bqn_evalCStr(input_string);
    BQN_EXP BQNV res = bqn_call1(xpr, bqn_arr);

    if (bqn_type(res) == 1){
        return PyLong_FromLong(bqn_toF64(res));
    } else if (bqn_type(res) == 0 ) {

        size_t rrank = bqn_rank(res);
        size_t rshape[rrank];    
        bqn_shape(res, rshape);

        npy_intp res_dims[1] = {rshape[0]}; // {10};  // 1D array of length 10

        PyObject* numpy_array_res = PyArray_SimpleNew(1, res_dims, NPY_INT);
        int* array_data_res = (int*)PyArray_DATA((PyArrayObject*)numpy_array);

        bqn_readI32Arr(res, array_data_res);
        bqn_free(res);
        Py_INCREF(numpy_array_res);
        return Py_BuildValue("O", numpy_array_res);

    } else {
        return NULL;
    }

}

static PyObject* check_array_type(PyObject* self, PyObject* args) {
    PyObject* numpy_array;

    // Parse the input, expecting a NumPy array
    if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &numpy_array)) {
        return NULL;
    }

    // Get the type of the NumPy array
    int array_type = PyArray_TYPE((PyArrayObject*)numpy_array);
    // NPY_INT

    // Return the array type as an integer
    return Py_BuildValue("i", array_type);
}

// Define the methods that will be available in the Python module
static PyMethodDef BqnMethods[] = {
    {"call", pybqn_call, METH_VARARGS, "Evaluate BQN code and return the result as array"},
    {"check_array_type", check_array_type, METH_VARARGS, "Check and return the type of a NumPy array"},
    {NULL, NULL, 0, NULL}
};

// Define the Python module
static struct PyModuleDef bqnmodule = {
    PyModuleDef_HEAD_INIT,
    "bqn",               // Module name
    NULL,                // Module documentation
    -1,                  // Size of per-interpreter state of the module
    BqnMethods
};

// Initialize the module
PyMODINIT_FUNC PyInit_bqn(void) {
    import_array();  // Initialize numpy C-API
    bqn_init();
    return PyModule_Create(&bqnmodule);
}

/*
To Compile the extension on Linux run

clear & rm ./bqn.so & gcc -shared -o bqn.so -g -fPIC bqn.c -I$HOME/miniconda3/envs/py310/include/python3.10 -I$HOME/miniconda3/envs/py310/lib/python3.10/site-packages/numpy/core/include -I/media/mu6mula/Data/work/BQN/CBQN-dzaima/include -Wl,-rpath=/media/mu6mula/Data/work/BQN/CBQN-dzaima -lcbqn

*/

// export LD_LIBRARY_PATH=/media/mu6mula/Data/work/BQN/CBQN-dzaima:$LD_LIBRARY_PATH