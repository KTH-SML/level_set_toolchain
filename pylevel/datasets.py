#!/usr/bin/env python
""" Module defining exemplatory dataset usage.

    Author: Philipp Rothenhäusler, Stockholm 2021

"""

import os
import enum


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"


## Base class definition for enumeration definition of level sets
class LevelSet(enum.IntEnum):
    pass


## Example implementation of level sets for prominent dynamical systems
class LevelSetExample(LevelSet, enum.IntEnum):
    SVEA = 1
    Drone = 2
    DroneForesight = 3


cwd = os.path.dirname(os.path.abspath(__file__))
path = dict()
path[LevelSetExample.SVEA] = cwd + "/../resources/svea/TTR_and_grad.mat"
## Low resolution example reachable set
path[LevelSetExample.Drone] = cwd + "/../resources/quad4D/low_res_BRS.mat"
## Long horizon example reachable set (exemplifying the curse of dimensionality)
path[LevelSetExample.DroneForesight] = cwd + "/../resources/quad4D/BRS.mat"

string2levelset = dict()
string2levelset["svea"] = LevelSetExample.SVEA
string2levelset["drone"] = LevelSetExample.Drone

