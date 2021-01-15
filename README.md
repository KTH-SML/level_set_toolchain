# SML's Hamilton-Jacobi Reachability Analysis Starter Kit

In this repo, you'll find a starting toolchain for solving and working with
Hamilton-Jacobi reachability analysis.
In particular, you can use this repo to start solving for reachable sets of dynamical systems with strong guarantees.

To compute reachable sets, we use the Level Set Method for solving the
Hamilton-Jacobi-Isaacs (HJI) inequality, yielding us value functions whose zero
sublevel set corresponds to your desired reachable set.
Then, you save the solutions in MATLAB and can use the Python interface to access them.

## Overview
- [Setup](#setup)
- [MATLAB Toolbox documentation](https://www.cs.ubc.ca/~mitchell/ToolboxLS/toolboxLS-1.1.pdf).
- [Python examples](./examples)

## Setup
This repository consists of both a Python package and a MATLAB example script.
We first go through the setup and usage of the MATLAB Level Set Toolbox and then introduce our Python wrapper with examples.

### MATLAB - Computing reachable sets
For detailed documentation about boundary conditions, general notation and usage of the MATLAB toolbox, please refer to [Documentation of MATLAB Toolbox](https://www.cs.ubc.ca/~mitchell/ToolboxLS/toolboxLS-1.1.pdf).


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

### Python - Using levelsets
In order to globally install the Python package referencing the local `resources` directory execute the following in the root directory of this repository
```bash
pip install -e .
```

**Basic package structure:**

Since it is typically inconvenient to use MATLAB in most robotics or hardware-based control projects, we have written a simple Python interface for working with the output of the Level Set Toolbox and helperOC.
Once you have computed the reachable sets of interest, you can load them into Python using scipy's `loadmat` function and then contstruct a `GridData` object using the data.

You can find all Python classes in the package `pylevel`.
The package `pylevel` is composed of a wrapper, which is a subclass of the `loader` to load the ma file from MATLAB.
This wrapper class creates sublevel instances of the GridData class to facilitate convenient access to value functions across grid indices.

You can find some basic examples of how to use the `pylevel` package under `./examples`.


### Python - Add custom dataset
In order to add your own generated dataset simply follow the following steps.

1. Generate the dataset in MATLAB and store the `your_file.m` file under `./resources/your_name/your_file.m`
2. Add an entry to the Python module `datasets.py` in the `pylevel` package.
    - Add an enumeration entry with `YourName` and the next integer
    - Add a path entry from the new enumeration
3. Instantiate the Loader with the `dataset=pylevel.datasets.LevelSet.YourName` argument

All provided loader scripts will then automatically fetch the corresponding file whenever the loader receives your new `LevelSet` enumeration type as the argument `dataset`.

For usage examples of the Python wrapper see
- [Levelsets at time](examples/timed_levelsets.py)
- [Convexified levelset](examples/convexified.py)

## Contribution
If you have found things to improve of you have questions, please create a pull request to let us know.
