#!/usr/bin/env python

import os
import enum


__license__ = "MIT"
__author__ = "Philipp Rothenhäusler"
__email__ = "phirot@kth.se "
__status__ = "Development"


class LevelSet(enum.IntEnum):
    SVEA = 1
    Drone = 2


cwd = os.path.dirname(os.path.abspath(__file__))
path = dict()
path[LevelSet.SVEA] = cwd + "/../resources/svea/TTR_and_grad.mat"
path[LevelSet.Drone] = cwd + "/../resources/quad4D/low_res_BRS.mat"

string2levelset = dict()
string2levelset["svea"] = LevelSet.SVEA
string2levelset["drone"] = LevelSet.Drone

