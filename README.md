# SML's Hamilton-Jacobi Reachability Analysis Toolchain
In this repository we introduce the toolchain for using _Hamilton-Jacobi Reachability_ through a combination of MATLAB and Python, allowing to solve for reachable sets of dynamical systems with strong guarantees.

We compute reachable sets using the Level Set Method to solve the Hamilton-Jacobi-Isaacs (HJI) inequality, yielding us value functions whose zero sublevel set corresponds to your desired reachable set.
Then, you save the solutions in MATLAB and can use the Python interface wrapper to access them convenient and efficiently during runtime.

## Overview
- [Setup](#setup)
- [MATLAB Toolbox documentation](https://www.cs.ubc.ca/~mitchell/ToolboxLS/toolboxLS-1.1.pdf).
- [Python example scripts](./scripts)

## Setup
This repository consists of both a Python package and a MATLAB example script.
We first go through the setup and usage of the `MATLAB Level Set Toolbox` and then introduce our `Python wrapper` with examples.

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

### Python - Using level sets
In order to globally install the Python package referencing the local `resources` directory execute the following in the root directory of this repository
```bash
pip install -e .
```

The package `pylevel` is composed of a wrapper, which provides convenience methods such as
- `is_member`: to check if a state is in any of the level sets
- `get_reachable_set`: Returns the minimal time to reach level set (Rounds state to next grid state)
- `get_reachable_set_at_time`: Returns the level set at specified or closest discretised time index

_Note: For all set retrieval methods it is possible to specify the `convexified=True` argument to receive only the vertices of the level sets convex hull._

You can find some basic examples of how to use the `pylevel` package under `./scripts`.


### Python - Define custom level sets
In order to access the level set wrapper from an external project it is recommended to define a `enum.IntEnum` to path `string` structured module such as the `pylevel.datasets` module.
But instead with the module located in your external package for example `your_package/sets.py`, in which you now only have to `import pylevel` to access the datasets `LevelSet` type and define the following structure.

```python
import pylevel


## Example implementation of level set type declaration
class LevelSet(pylevel.datasets.LevelSet):
    YourLevelSetName = 1


## Note that here the LevelSet name and the *.mat file name do not need to coincide.
cwd = os.path.dirname(os.path.abspath(__file__))
path = dict()
path[LevelSet.YourLevelSetName] = cwd + "/../resources/YourLevelSetName.mat"

string2levelset = dict()
string2levelset["your_config_string_name"] = LevelSet.YourLevelSetName
```

In your package this would look something like this

```python
import pylevel


from your_module.sets import path
from your_module.sets import LevelSet


if __name__ == "__main__":
    level_set_type = LevelSet.YourLevelSetName

    wrapper = pylevel.wrapper.LevelSetWrapper(
            label="ExampleLevelSet",
            path=path[level_set_type])
```

_Note: Here the `string2levelset` allows to potentially fetch string arguments from `*.yaml` or `*.json` configurations (as usually used in ROS packages) and the `LevelSetExample` allows to programatically use specific level set wrappers avoiding stringified conditions for `IntelliSense`._

For usage examples of the Python wrapper see the scripts directory
- [Levelsets at time](scripts/timed_level_sets.py)


## Contribution
If you have found things to improve or you have questions, please create a pull request to let us know.


## LICENSE
See the `LICENSE` file for details of the available open source licensing.
