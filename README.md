# Hamilton-Jacobi Reachability Analysis Toolchain
In this repository we introduce the toolchain for using _Hamilton-Jacobi Reachability_ through a combination of MATLAB and Python, allowing to solve for reachable sets of dynamical systems with strong guarantees.

We compute reachable sets using the Level Set Method to solve the Hamilton-Jacobi-Isaacs (HJI) inequality, yielding us value functions whose zero sublevel set corresponds to your desired reachable set.
Then, you save the solutions in MATLAB and can use the Python interface wrapper to access them convenient and efficiently during runtime.

## Overview
- [Setup](#setup)
- [MATLAB Toolbox documentation](https://www.cs.ubc.ca/~mitchell/ToolboxLS/toolboxLS-1.1.pdf).
- [Python example scripts](./scripts)
- [Python API](https://kth-sml.github.io/level_set_toolchain/) (And extended usage documentation)

## Setup
This repository consists of both a Python package and a MATLAB example script.
We first go through the setup and usage of the `MATLAB Level Set Toolbox` and then introduce our `Python wrapper` with examples.

### MATLAB - Computing reachable sets
For detailed documentation about boundary conditions, general notation and usage of the MATLAB toolbox, please refer to the [documentation of MATLAB Toolbox](https://www.cs.ubc.ca/~mitchell/ToolboxLS/toolboxLS-1.1.pdf).


Currently, the most stable toolbox for computing solutions to the HJI inequality
is still the Level Set Toolbox. To start computing reachable sets with the Level
Set Toolbox, start by getting it from Ian Mitchell's page:

[https://www.cs.ubc.ca/~mitchell/ToolboxLS/](https://www.cs.ubc.ca/~mitchell/ToolboxLS/)

Then, clone the helper repository from UC Berkeley's Hybrid Systems Lab:

```bash
git clone https://github.com/HJReachability/helperOC
```

Finally, in MATLAB, add both `toolboxls` and `helperOC` to your MATLAB path.
With this you are already set up to solve the HJI inequalities.
We have provided examples of how to use the libraries to solve HJI inequalities for the SML's SVEA vehicle and a quadrotor that is constrained to hovering in a 2D plane.
For either example, add the respective folder to your MATLAB path, and run `compute_RS.m`.
This script will save the information required to extract out the reachable sets into an approriately named folder in `cached_rs`.

These examples have presets just to be illustrative, go ahead and change them
to match the requirements of your project.

### Python - Using level sets
Fetch necessary dependencies with
```bash
pip install -r requirements.txt
```
and install the package using the `setup.py` with
```bash
python setup.py install
```

_Note: If you are a developer and you plan to iterate code changes, use `./init.sh` in the root of the repository to expose the source code as a package to the PYTHONPATH.
This allows you to use latest code changes without repeated installation through `setup.py`._

**Documentation of the Python API**:

The API documentation of the Python wrapper can be found [here](https://kth-sml.github.io/level_set_toolchain/).

You can find some basic examples of how to use the `pylevel` package under `./scripts`. This includes access of reachable sets at a specified time or for example the usage of the import and export feature avoiding repeated initialisation.



## Contribution
If you have found things to improve or you have questions, please create a pull request to let us know.


## LICENSE
See the `LICENSE` file for details of the available open source licensing.
