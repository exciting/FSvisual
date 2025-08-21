from fermisurface import FermiSurface
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument( "bxsf_files_directory", help="directory (folder) where the .bxsf files (Fermi"
                                                         "surface files) are stored")
parser.add_argument("save_fermisurfaces", help="directory where visualized Fermi surfaces "
                                                       "are stored")

# optional arguments

parser.add_argument("-s","--subdivision_surface", help="divides every triangle of the Fermi surface mesh"
                                                       " into two triangles; executes as many times as the input says",
                    default=0, type=int)

parser.add_argument("-d","--downsampling_surface", help="lowers the resolution of the "
                                                        "Fermi surface mesh (number of faces) to a given percentage "
                                                        "(from original face count)",default=100, type=int)

parser.add_argument("-c","--create_SVG", help="downsamples the surface by a given percentage",
                    action="store_true")

args = parser.parse_args()

# auch für einzelne files anpassen
for filename in os.listdir(args.bxsf_files_directory):
    filepath = os.path.join(args.bxsf_files_directory, filename)
    # check if path leads to file
    if not os.path.isfile(filepath):
        continue

    new_fermisurface = FermiSurface()

    if args.subdivision_surface != 0 and args.downsampling_surface != 100:
        raise ValueError("subdivision_surface and downsampling_surface are contrary functions")

    new_fermisurface.build_surface_with_bxsf_files(filepath, args.subdivision_surface, args.downsampling_surface)
    new_fermisurface.visualization(filepath, args.save_fermisurfaces, svg=args.create_SVG)

