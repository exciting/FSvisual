from .fermisurface import FermiSurface
import os
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument( "bxsf_files_directory", help="directory (folder) where the .bxsf files (Fermi"
                                                             "surface files) are stored")

    # optional arguments

    parser.add_argument("-sf","--save_fermisurfaces", help="directory where visualized Fermi surfaces "
                                                           "are stored")

    parser.add_argument("-s","--subdivision_surface", help="divides every triangle of the Fermi surface mesh"
                                                           " into two triangles; executes as many times as the input says",
                        default=0, type=int)

    parser.add_argument("-dp","--downsampling_surface_percentage", help="lowers the resolution of the "
                                                            "Fermi surface mesh (number of faces) to a given percentage "
                                                            "(from original face count)",default=100, type=int)

    parser.add_argument("-df","--downsampling_surface_face", help="lowers the resolution of the "
                                                            "Fermi surface mesh (number of faces) to a given face number",
                        default=None, type=int)


    parser.add_argument("-c","--create_SVG", help="boolean whether to create SVG files ",
                        action="store_true")

    args = parser.parse_args()

    # you can either parse a whole directory of .bxsf files or just the path to a single .bxsf file
    file_list = []
    if os.path.isfile(args.bxsf_files_directory):
        file_list.append(os.path.basename(args.bxsf_files_directory))
        path = os.path.dirname(args.bxsf_files_directory)
        if args.save_fermisurfaces is not None:
            save_path = args.save_fermisurfaces
        else:
            save_path = path
    else:
        file_list.extend(os.listdir(args.bxsf_files_directory))
        path = args.bxsf_files_directory
        if args.save_fermisurfaces is not None:
            save_path = args.save_fermisurfaces
        else:
            save_path = args.bxsf_files_directory

    for filename in file_list:
        filepath = os.path.join(path, filename)
        # check if path leads to file
        if not os.path.isfile(filepath):
            continue

        new_fermisurface = FermiSurface()

        if args.subdivision_surface != 0 and args.downsampling_surface != 100:
            raise ValueError("subdivision_surface and downsampling_surface are contrary functions")

        new_fermisurface.build_surface_with_bxsf_files(filepath, args.subdivision_surface,
                                                       args.downsampling_surface_percentage, args.downsampling_surface_face)

        new_fermisurface.visualization(filepath, save_path, svg=args.create_SVG)

if __name__ == "__main__":
    main()
