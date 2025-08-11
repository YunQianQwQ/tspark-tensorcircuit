#include <pybind11/pybind11.h>
#include <string>

namespace py = pybind11;

static std::string process(const std::string& s) {
    return s;
}

PYBIND11_MODULE(mylib, m) {
    m.doc() = "pybind11 single-file example";
    m.def("process", &process, py::arg("s"));
}