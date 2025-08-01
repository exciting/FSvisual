from visualisation import plot
from input import read_energy_numbers
import numpy as np
from Fermisurface_class import FermiSurface


def main(filepath, save_fermisurf_path):

    data = read_energy_numbers(filepath)

    new_fermisurface = FermiSurface(data[0], data[1], data[2], data[3])
    new_fermisurface.set_brillouin_zone()

    grid_size = new_fermisurface.grid_size
    new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])

    fermi_surface_list = []
    band_index = []
    for index, columnName in enumerate(new_fermisurface.energy_values.columns):

        # Apply the Marching Cubes algorithm
        try:
            new_fermisurface.marching_cubes(columnName)
        except ValueError:
            "nothing here"
            continue

        band_index.append(index + 1)  # for the plot

        # transform vertices, so it fits the base_vect_grid

        new_fermisurface.subdivide_surface(2)

        # translation and shrinkage

        # 2 wegen Durchmesser 1. BZ  # nochmal gucken.

        new_fermisurface.scale_surface(2 / new_basevect_grid_size)

        # translation

        new_fermisurface.center_surface()

        new_fermisurface.slice_surface()

        fermi_surface_list.append(new_fermisurface.surface)

    # visualization
    plot(fermi_surface_list, new_fermisurface.brillouin_zone, band_index, filepath, save_fermisurf_path)
