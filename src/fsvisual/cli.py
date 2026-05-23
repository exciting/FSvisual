from .fermisurface import FermiSurface
import os
import argparse
from rich import print as rprint
from rich.progress import Progress
import time

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

    parser.add_argument("-wl","--width_line_BZ", help="adjusts the width of the Brillouin zone lines ",
                        default=2, type=int)

    parser.add_argument("-c", "--create_SVG", help="boolean whether to create SVG files ",
                        action="store_true")

    parser.add_argument("-f", "--force", help="if bandstructure files do not end with .bxsf, but "
                                              "are still correctly formatted, forcing FSvisual "
                                              "to parse those files is possible ",
                        action="store_true")

    args = parser.parse_args()

    # you can either parse a whole directory of .bxsf files or just the path to a single .bxsf file
    file_list = []
    is_directory = False
    if os.path.isfile(args.bxsf_files_directory):
        file_list.append(os.path.basename(args.bxsf_files_directory))
        path = os.path.abspath(os.path.dirname(args.bxsf_files_directory))
        if args.save_fermisurfaces is not None:
            save_path = args.save_fermisurfaces
        else:
            save_path = path
    else:
        is_directory = True
        file_list.extend(file_ for file_ in os.listdir(args.bxsf_files_directory) if (file_.endswith('.bxsf')) or args.force)
        path = args.bxsf_files_directory
        if args.save_fermisurfaces is not None:
            save_path = args.save_fermisurfaces
        else:
            save_path = args.bxsf_files_directory

    if len(file_list) == 1 and not is_directory:
        rprint("Starting visualization of Fermi surface...")
    elif len(file_list) >= 1:
        rprint(f"Starting visualization of {len(file_list)} Fermi surfaces...")
    else:
        rprint(f"[yellow]No suitable files where found in {args.bxsf_files_directory}[/yellow]")

    for i, filename in enumerate(file_list):
        filepath = os.path.join(path, filename)
        # check if path leads to file
        if not os.path.isfile(filepath):
            continue

        process_string = ""

        if len(file_list) == 1:
            process_string = "Processing..."
            #process_string = "Test Processing..."   
        else:
            process_string = f"[{i+1}/{len(file_list)}] Processing..."

        with Progress() as progress:
            task = progress.add_task(process_string, total=100)

            new_fermisurface = FermiSurface()
            progress.update(task, advance=10)

            if args.subdivision_surface != 0 and args.downsampling_surface != 100:
                raise ValueError("subdivision_surface and downsampling_surface are contrary functions")

            new_fermisurface.build_surface_with_bxsf_files(filepath, progress, task, args.subdivision_surface,
                                                        args.downsampling_surface_percentage,
                                                        args.downsampling_surface_face)

            new_fermisurface.visualization(filepath, save_path, svg=args.create_SVG, width_line_bz=args.width_line_BZ)
            progress.update(task, advance=10)
            rprint("[green]Successfully created visualization![/green]")

if __name__ == "__main__":
    main()
