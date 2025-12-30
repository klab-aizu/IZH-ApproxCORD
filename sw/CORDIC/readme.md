# Install approximate adder in evoapproxlib

## Download EvoApproxLib Source Code

Go to the following link: https://github.com/ehw-fit/evoapproxlib/tree/v2022
Then:

1. Click **Code → Download ZIP**
2. Extract the ZIP file to a directory

## Install Visual C++ Build Tools (Required)

EvoApproxLib contains C/C++ code that must be compiled.

Download Visual C++ Build Tools from:
https://visualstudio.microsoft.com/visual-cpp-build-tools/

During installation:

  Select C++ build tools

  Make sure the following components are checked:

    MSVC v14x build tools

    Windows 10/11 SDK

After installation, restart your computer (recommended).

## Install Required Python Packages

Open Command Prompt or Anaconda Prompt and run:
```bash
pip install cython
```
Check your Python version:

```bash
python --version
```
Recommended: Python 3.8 – 3.11 (64-bit)

## Generate Cython Sources

Navigate to the EvoApproxLib directory:
```bash
cd D:\evoapproxlib
```
Run:
```bash
python make_cython.py
```
This will generate a new directory

## Compile EvoApproxLib

Go into the cython directory:
```bash
cd cython
```
Run:
```bash
python setup.py build_ext
```
Compilation may take several minutes.

## Simple Usage Example

```python
import evoapproxlib as eal

a = 123
b = 77

exact = a + b
approx = eal.add16se_2TN.calc(a, b)

print("Exact :", exact)
print("Approx:", approx)
print("Error :", approx - exact)
```
If no error occurs, the installation was successful
