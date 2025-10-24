from fsvisual.fermisurface import FermiSurface
from fsvisual.input import read_energy_numbers
import pytest
import trimesh
import numpy as np


@pytest.fixture
def calc_fermisurface():
    """Creates a fresh instance of FermiSurface before each test."""
    data_fermisurf = read_energy_numbers("tests/data/bxsf/Ag_fcc_5x5x5.bxsf")
    my_surface = FermiSurface()
    my_surface.set_energy_values(data_fermisurf[0])
    my_surface.set_fermi_energy(data_fermisurf[1])
    my_surface.set_rez_base_vect(data_fermisurf[2])
    my_surface.set_k_grid_by_size(data_fermisurf[3])
    return my_surface

def test_marching_cube(calc_fermisurface):

    expected_fermisurface = trimesh.load("tests/data/FermiSurface/mc_surface.ply")

    column = calc_fermisurface.energy_values.columns[3]
    calc_fermisurface.marching_cubes(column)

    assert np.allclose(expected_fermisurface.vertices, calc_fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, calc_fermisurface.surface.faces)

def test_scale_surface(calc_fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/scale_surface.ply")

    with pytest.raises(ValueError, match="surface is not yet defined"): calc_fermisurface.scale_surface(5)

    column = calc_fermisurface.energy_values.columns[3]
    calc_fermisurface.marching_cubes(column)

    grid_size = calc_fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
    calc_fermisurface.scale_surface(2 / new_basevect_grid_size)

    assert np.allclose(expected_fermisurface.vertices, calc_fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, calc_fermisurface.surface.faces)

def test_center_surface(calc_fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/center_surface.ply")

    with pytest.raises(ValueError, match="surface is not yet defined"): calc_fermisurface.center_surface()
    column = calc_fermisurface.energy_values.columns[3]
    calc_fermisurface.marching_cubes(column)
    calc_fermisurface.center_surface()

    assert np.allclose(expected_fermisurface.vertices, calc_fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, calc_fermisurface.surface.faces)

def test_slice_surface(calc_fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/slice_surface.ply")

    with pytest.raises(ValueError, match="Brillouin Zone is not yet defined"): calc_fermisurface.slice_surface()
    #with pytest.raises(ValueError, match="surface is not yet defined"): calc_fermisurface.slice_surface()
    column = calc_fermisurface.energy_values.columns[3]
    calc_fermisurface.marching_cubes(column)


    calc_fermisurface.center_surface()

    grid_size = calc_fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
    calc_fermisurface.scale_surface(2 / new_basevect_grid_size)

    calc_fermisurface.compute_brillouin_zone()
    calc_fermisurface.slice_surface()
    print(calc_fermisurface.surface)

    assert np.allclose(expected_fermisurface.vertices, calc_fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, calc_fermisurface.surface.faces)