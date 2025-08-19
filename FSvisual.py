from input import read_energy_numbers
from fermisurface import FermiSurface
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument( "bxsf_files_directory", help="directory (folder) where the .bxsf files (Fermi"
                                                         "surface files) are stored")
parser.add_argument("save_fermisurfaces", help="directory where visualized Fermi surfaces "
                                                       "are stored")

# optional arguments

parser.add_argument("-s","--subdivision_surface", help="divides every triangle of the surface into two "
                                                       "triangles; executes as many times as the input says", type=int)

parser.add_argument("-d","--downsampling_surface", help="downsamples the surface by a given percentage"
                    , type=int)

parser.add_argument("-c","--create_SVG", help="downsamples the surface by a given percentage"
                    ,action="store_true")

args = parser.parse_args()

for filename in os.listdir(args.bxsf_files_directory):
    filepath = os.path.join(args.bxsf_files_directory, filename)
    # check if path leads to file
    if not os.path.isfile(filepath):
        continue

    new_fermisurface = FermiSurface()
    new_fermisurface.build_surface_with_bxsf_files(filepath)
    new_fermisurface.visualization(filepath, args.save_fermisurfaces)

