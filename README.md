# SML's Hamilton-Jacobi Reachability Analysis Starter Kit

In this repo, you'll find a starting toolchain for solving and working with
Hamilton-Jacobi reachability analysis.
In particular, you can use this repo to start solving for reachable sets of dynamical systems with strong guarantees.

To compute reachable sets, we use the Level Set Method for solving the
Hamilton-Jacobi-Isaacs (HJI) inequality, yielding us value functions whose zero
sublevel set corresponds to your desired reachable set.
Then, you save the solutions in MATLAB and can use the Python interface to access them.

## Computing reachable sets with the Level Set Method in MATLAB

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

## Working with computed solutions in Python

Since it is typically inconvenient to use MATLAB in most robotics or hardware-based control projects, we have written a simple Python interface for working with the output of the Level Set Toolbox and helperOC.
Once you have computed the reachable sets of interest, you can load them into Python using scipy's `loadmat` function and then contstruct a `GridData` object using the data.
The `GridData` class is defined in `py_interface/grid.py`.
In addition to allowing you to access the data in the MATLAB outputs, the `GridData` also includes some methods for interporating the data, computing the sub- or super-level sets (which correspond to reachable sets, depending on your formulation), etc. Again, we have provided a basic example of using the `GridData` class on varying reachable set representations. See `py_interface/rs_example.py` for more details.


### Setup

In order to globally install the Python package referencing the local `resources` directory execute
```bash
pip install -e .
```


### Add custom dataset
In order to add your own generated dataset simply follow the following steps.

1. Generate the dataset in MATLAB and store the `your_file.m` file under `./resources/your_name/your_file.m'
2. Add an entry to the Python module 'datasets.py' in the 'pylevel' package.
    - Add an enumeration entry
    - Add a path entry from the new enumeration

All provided loader scripts will then automatically fetch the corresponding file whenever the loader receives your new `LevelSet` enumeration type as argument.
