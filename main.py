from brilouin_zone import first_bz
from mesh_algorythms import scale, centering, face_center_BZ
from visualisation import plot
from input import read_energy_numbers
import numpy as np
import trimesh
from skimage import measure
import pymeshlab
from copy import deepcopy
from Fermisurface_class import FermiSurface


def main(filepath, save_fermisurf_path):
    data = read_energy_numbers(filepath)
    # coordinates of the first Brillouin zone

    new_fermisurface = FermiSurface(data[0], data[1], data[2], data[3])
    new_fermisurface.set_brillouin_zone()

    new_cartesian_mesh = new_fermisurface.cartesian_mesh()
    grid_size = new_fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
    fermi_surface_list = []

    band_index = []
    for index, columnName in enumerate(new_fermisurface.energy_values.columns):

        new_cart_mesh_helper = deepcopy(new_cartesian_mesh)
        # creates an array with energies taken by the corresponding indices of new_cart_mesh_helper -> created array is
        # as big as the indexing array
        new_cart_mesh_helper = new_fermisurface.energy_values[columnName][new_cart_mesh_helper.astype(int)]
        new_cart_mesh_helper = np.array(new_cart_mesh_helper).reshape(
            (new_basevect_grid_size[0], new_basevect_grid_size[1],
             new_basevect_grid_size[2]))
        print("done")

        # Apply the Marching Cubes algorithm
        try:
            vertices, faces, normals, values = new_fermisurface.marching_cubes(new_cart_mesh_helper)
        except ValueError:
            "nothing here"
            continue

        band_index.append(index + 1)  # for the plot

        # transform vertices, so it fits the base_vect_grid

        fermi_surface = new_fermisurface.subdivide_surface(vertices, faces, 2)

        # translation and shrinkage
        # scales surface to the size of the brillouin zone
        fermi_surface = scale(2 / new_basevect_grid_size, fermi_surface)

        # translation
        fermi_surface = centering(fermi_surface)
        new_fermisurface.set_surface(fermi_surface)

        new_fermisurface.slice_surface()

        fermi_surface_list.append(new_fermisurface.surface)

    # visualization
    plot(fermi_surface_list, new_fermisurface.brillouin_zone, band_index, filepath, save_fermisurf_path)
