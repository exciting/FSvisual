from input import read_energy_numbers
from fermisurface import FermiSurface


def main(filepath, save_fermisurf_path):

    data = read_energy_numbers(filepath)

    new_fermisurface = FermiSurface(data[0], data[1], data[2], data[3])
    new_fermisurface.compute_brillouin_zone()

    new_fermisurface.build_surface_with_bxsf_files()
    new_fermisurface.visualization(filepath, save_fermisurf_path)
