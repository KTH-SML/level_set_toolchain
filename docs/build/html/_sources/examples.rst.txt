Examples
===============

Creating new enumeration identifiers
-------------------------------------

To be documented


Levelset access
-------------------------------------

To be documented


Import and Export for improved initialisation
----------------------------------------------

In order to accelerate the initialisation the export feature can be utilised to avoid the building process of the reachable set dictionaries.

.. code-block:: python
    :linenos:


    #!/usr/bin/env python
    """ Example for level set wrapper usage.

        Author: Philipp Rothenhäusler, Stockholm 2020

    """


    import numpy


    import pylevel


    LABEL = "ExampleLevelSet"
    FROM_MEMORY = True
    EXEMPLIFY_DEBUG_VERBOSITY = True

    if __name__ == '__main__':
        level_set_type = pylevel.datasets.LevelSetExample.Drone

        if not FROM_MEMORY:
            wrapper = pylevel.wrapper.ReachableSetWrapper(
                    label=LABEL,
                    path=pylevel.datasets.path[level_set_type],
                    debug_is_enabled=EXEMPLIFY_DEBUG_VERBOSITY)
            wrapper.export()
        else:
            wrapper = pylevel.wrapper.ReachableSetWrapper(
                    label=LABEL,
                    from_memory=".",
                    debug_is_enabled=EXEMPLIFY_DEBUG_VERBOSITY)

            ## Time steps from final time tf to t0
            t_idx = list(wrapper.time)
            t_idx.reverse()

            ## Time indexed access of levelsets
            levelsets_states = [wrapper.reach_at_t(t) for t in t_idx]
            for levelset_states, t in zip(levelsets_states,t_idx):
                states_sliced = numpy.hstack([
                    levelset_states[:, [0]],
                    levelset_states[:, [2]]])
                pylevel.utilities.visualise_2d(wrapper, states_sliced, t, show=False, show_image=False)
                pylevel.utilities.show_plots_for_time(time_in_seconds=.5)

            pylevel.utilities.show_plots()

