#!/usr/bin/env python

import numpy
import typing
import matplotlib
import matplotlib.pyplot as plt

DEBUG_IS_ENABLED = True


## Define constants
dx = numpy.array([1, 2])
index_max = numpy.array([9, 9])
index_min = numpy.array([0, 0])


## Configuration for 2D example:
## Select axes dimension
AXES = [0, 1]
## Indices
indices = numpy.array([
        ## All inadmissible
        [9, 3],
        ## Partially inadmissible
        [0, 0],
        ## All admissible
        [3, 4],
        ## Partially inadmissible
        [9, 11],
        ## All inadmissible
        [11, 11],
        ## All admissible
        [9, 9],
        ])


## TODO: Create convex test value_function
## Indices along x
b = numpy.pi/3
ix = numpy.linspace(-b, b, 10)
## Generate 2d grid
xy, yx = numpy.meshgrid(ix, ix)
zz = numpy.sin((xy**2 + yx**2)**.5)

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
ax.plot_surface(xy, yx, zz)  #  cmap=matplotlib.cm.coolwarm)
# plt.show()

value_function = zz


def _index_in_grid(index):
    """ Return true if all elements satisfy grid resolution. """
    global dx
    global index_max

    return (index_min <= index).all() and (index <= index_max).all()


def test_index_lookup(index, axes : typing.List[int], return_offset=False):
    # apply offset mask to current index and check if they are in grid
    ## TODO: drone state space specific implementation
    ## 4D example
    # indices_offset = numpy.array([
    #                     [-1, 0, 0, 0],
    #                     [1, 0, 0, 0],
    #                     [0, 0, -1, 0],
    #                     [0, 0, 1, 0]])
    indices_offset = numpy.array([
        [-1, 0],
        [1, 0],
        [0, -1],
        [0, 1],
        ])

    indices = numpy.add(index, indices_offset)
    #print('Offset indices: ', indices)
    ## TODO: Verify that indices are in grid
    ## TODO: Verify that index in grid
    ## How to drop
    indices_mask = numpy.apply_along_axis(_index_in_grid, arr=indices, axis=1)
    #print('Indices mask: ', indices_mask)

    if return_offset:
        return indices[indices_mask], indices_offset[indices_mask]
    return indices[indices_mask]

def test_gradient(index):
    global DEBUG_IS_ENABLED
    global AXES

    ## With state input usually
    # index = self.grid.index(state)

    ## Current state value function
    if not _index_in_grid(index):
        return
    v = value_function[tuple(index)]

    ## Admissible neighbour indices and their delta
    indices, indices_delta = test_index_lookup(
            index, axes=AXES, return_offset=True)

    if DEBUG_IS_ENABLED:
        print('--> Index ({}) has {} neighbours: \n{}\n'.format(
             index, len(indices), indices))

    ## di x 1 : scalar spatial magnitude for each index
    dsi = numpy.linalg.norm(indices_delta * dx, axis=1)
    ## di x 1 : value function differential for each index
    vs = numpy.apply_along_axis(
            lambda index: value_function[tuple(index)] - v, arr=indices, axis=1)
    ## di x 1 / di x 1 : gradient for each index based on its spatial magnitude
    gs = numpy.divide(vs, dsi)

    return numpy.max(gs)


if __name__ == "__main__":
    for it, index in enumerate(indices):
        print('Test {}'.format(it))
        g = test_gradient(index)
        print('Gradient: {}'.format(g))

