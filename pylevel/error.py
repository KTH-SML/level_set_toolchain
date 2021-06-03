#!/usr/bin/env python
""" Error module with exception specification.
 
    Note:
        Verbosify output using debug_is_enabled on
        initialisation.

"""


class StateLookupError(Exception):
    """ Failed to find index for state. """
    pass


class StateNotReachableError(Exception):
    """ Provided state could not be found in reachable set. """
    pass


class IndexNotInGridError(StateNotReachableError):
    """ Error for index not in specified grid range. """
    pass


class IndexHasNoValidNeighboursError(Exception):
    """ Search for valid neighbouring indices failed. """
    pass


