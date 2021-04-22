Examples
===============

Creating new level set types
-------------------------------------

In order to access the level set wrapper from an external project it is recommended to define a ``enum.IntEnum`` to path ``string`` structured module such as the ``pylevel.datasets`` module.
But instead with the module located in your external package for example ``your_package/sets.py``, in which you now only have to ``import pylevel`` to access the datasets ``LevelSet`` type and define the following structure.

.. code-block:: python
    :linenos:

    #!/usr/bin/env python

    # your_package/sets.py

    import pylevel


    ## Example implementation of level set type declaration
    class LevelSet(pylevel.datasets.LevelSet, enum.IntEnum):
        YourLevelSetName = 1


    ## Note that here the LevelSet name and the *.mat file name do not need to coincide.
    cwd = os.path.dirname(os.path.abspath(__file__))
    path = dict()
    path[LevelSet.YourLevelSetName] = cwd + "/../resources/YourLevelSetName.mat"

    string2levelset = dict()
    string2levelset["your_config_string_name"] = LevelSet.YourLevelSetName

In a example script ``example.py`` using your package this would look something like this

.. code-block:: python
    :linenos:

    #!/usr/bin/env python

    # example.py

    import pylevel


    from your_package.sets import path
    from your_package.sets import LevelSet


    if __name__ == "__main__":
        level_set_type = LevelSet.YourLevelSetName

        wrapper = pylevel.wrapper.LevelSetWrapper(
                label="ExampleLevelSet",
                path=path[level_set_type])

Note: Here the `string2levelset` allows to potentially fetch string arguments from ``*.yaml`` or ``*.json`` configurations (as usually used in ROS packages) and the ``LevelSetExample`` allows to programatically use specific level set wrappers with support of ``IntelliSense``.


Import and Export for improved initialisation
----------------------------------------------

In order to accelerate the initialisation the export feature can be utilised to avoid the building process of the reachable set dictionaries on repeated script executions.


.. code-block:: python
    :linenos:


    #!/usr/bin/env python

    # scripts/export.py

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

