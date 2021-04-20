#!/usr/bin/env python


class StateLookupError(Exception):
    """ Failed to find index for state.

        Note:
            Verbosify output using debug_is_enabled on
            initialisation.
    """
    pass


class StateNotReachableError(Exception):
    """ Provided state could not be found in reachable set.

        Note:
            Verbosify output using debug_is_enabled on
            initialisation.
    """
    pass

