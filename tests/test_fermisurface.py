from fsvisual.fermisurface import FermiSurface
from fsvisual.input import read_energy_numbers
import pytest
import trimesh
import numpy as np
filepath = "tests/data/bxsf/Ag_fcc_5x5x5.bxsf"

@pytest.fixture
def fermisurface():
    """Creates a fresh instance of FermiSurface before each test."""
    data_fermisurf = read_energy_numbers(filepath)
    my_surface = FermiSurface()
    my_surface.set_energy_values(data_fermisurf[0])
    my_surface.set_fermi_energy(data_fermisurf[1])
    my_surface.set_rez_base_vect(data_fermisurf[2])
    my_surface.set_k_grid_by_size(data_fermisurf[3])
    return my_surface

def test_marching_cube(fermisurface):

    expected_fermisurface = trimesh.load("tests/data/FermiSurface/mc_surface.ply")

    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)

    assert np.allclose(expected_fermisurface.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, fermisurface.surface.faces)

def test_scale_surface(fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/scale_surface.ply")

    with pytest.raises(ValueError, match="surface is not yet defined"):
        fermisurface.scale_surface(5)

    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)

    grid_size = fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
    fermisurface.scale_surface(2 / new_basevect_grid_size)

    assert np.allclose(expected_fermisurface.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, fermisurface.surface.faces)

def test_center_surface(fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/center_surface.ply", process=False)

    with pytest.raises(ValueError, match="surface is not yet defined"): fermisurface.center_surface()
    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)
    fermisurface.center_surface()

    assert np.allclose(expected_fermisurface.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, fermisurface.surface.faces)

def test_slcie_surface_exception(fermisurface):
      with pytest.raises(ValueError, match="Brillouin Zone is not yet defined"):
        fermisurface.slice_surface()

def test_slice_surface(fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/slice_surface.ply", process=False)
    fermisurface.compute_brillouin_zone()
    with pytest.raises(ValueError, match="surface is not yet defined"):
        fermisurface.slice_surface()
    #with pytest.raises(ValueError, match="surface is not yet defined"): calc_fermisurface.slice_surface()
    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)


    fermisurface.center_surface()

    grid_size = fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
    fermisurface.scale_surface(2 / new_basevect_grid_size)
    fermisurface.slice_surface()

    assert np.allclose(expected_fermisurface.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, fermisurface.surface.faces)

def test_subdivide_surface(fermisurface):
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/subdivide_surface.ply", process=False)

    with pytest.raises(ValueError, match="surface is not yet defined"):
        fermisurface.subdivide_surface(1)
    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)

    fermisurface.subdivide_surface(1)

    assert np.allclose(expected_fermisurface.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, fermisurface.surface.faces)

expected_fermisurface1 = trimesh.load("tests/data/FermiSurface/downsample_70_None_surface.ply", process=False)
expected_fermisurface2 = trimesh.load("tests/data/FermiSurface/downsample_100_100_surface.ply", process=False)

@pytest.mark.parametrize("face_percentage, face_number, expected_mesh", [
    (70, None, expected_fermisurface1),
    (100, 100, expected_fermisurface2)
])

def test_downsample_surface(fermisurface, face_percentage, face_number, expected_mesh):

    with pytest.raises(ValueError, match="surface is not yet defined"):
        fermisurface.downsample_surface(70, None)
    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)

    fermisurface.downsample_surface(face_percentage, face_number)

    assert np.allclose(expected_mesh.vertices, fermisurface.surface.vertices)
    assert np.array_equal(expected_mesh.faces, fermisurface.surface.faces)

def test_downsample_surface_exception(fermisurface):

    column = fermisurface.energy_values.columns[3]
    fermisurface.marching_cubes(column)
    with pytest.raises(ValueError, match="You can only either provide a face_percentage or face_numbers, not both"):
        fermisurface.downsample_surface(70, 1000)

def test_build_surface():
    expected_fermisurface = trimesh.load("tests/data/FermiSurface/build_surface.ply", process=False)
    calc_fermisurface = FermiSurface()
    calc_fermisurface.build_surface_with_bxsf_files(filepath)

    assert np.allclose(expected_fermisurface.vertices, calc_fermisurface.surface.vertices)
    assert np.array_equal(expected_fermisurface.faces, calc_fermisurface.surface.faces)