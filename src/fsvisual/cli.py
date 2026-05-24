from .fermisurface import FermiSurface
import os
import argparse
from rich import print as rprint
from rich.progress import Progress, BarColumn, TextColumn, TaskProgressColumn
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

    parser.add_argument("--force", help="if bandstructure files do not end with .bxsf, but "
                                              "are still correctly formatted, forcing FSvisual "
                                              "to parse those files is possible ",
                        action="store_true")

    parser.add_argument("--dont_save", help="Deactivates saving Fermi surfaces to file",
                        action="store_false", default=True)

    parser.add_argument("--show", help="Fermi surfaces are immediately shown in Browser",
                        action="store_true")

    parser.add_argument("--dont_show", help="Deactivates the default, that if only 1 Fermi surface "
                                            "is created, it is always shown in Browser",
                        action="store_false", default=True)


    args = parser.parse_args()

    if not args.dont_save:
        args.show = True

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

    success = 0
    for i, filename in enumerate(file_list):
        filepath = os.path.join(path, filename)
        # check if path leads to file
        if not os.path.isfile(filepath):
            continue

        if len(file_list) == 1:
            process_string = "Processing..."

        else:
            process_string = f"[{i+1}/{len(file_list)}] Processing..."

        fig = 0
        with Progress(TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn()) as progress:
            timings = [5, 35, 4, 2, 24, 0, 0, 0, 26, 4]

            task = progress.add_task(process_string, total=100)

            new_fermisurface = FermiSurface()


            if args.subdivision_surface != 0 and args.downsampling_surface != 100:
                raise ValueError("subdivision_surface and downsampling_surface are contrary functions")

            new_fermisurface.build_surface_with_bxsf_files(filepath, args.subdivision_surface,
                                                           args.downsampling_surface_percentage,
                                                           args.downsampling_surface_face, progress=progress,
                                                           task=task, timings=timings)

            fig = new_fermisurface.visualization(filepath, save_path, svg=args.create_SVG,
                                                 width_line_bz=args.width_line_BZ, save_fs=args.dont_save)
            progress.update(task, advance=timings[9])

        if (len(file_list) == 1 or args.show) and args.dont_show:
            fig.show()

        filename = os.path.basename(filepath)
        filename = filename.split(".")[0]

        if os.path.isfile(f'{save_path}/{filename}.html'):
            rprint("Success!")
            success += 1

    if success == len(file_list) and len(file_list) >= 1:
        rprint(f"[green]Created [{success}/{len(file_list)}] visualizations![/green]")
    elif len(file_list) >= 1 and not args.dont_save:
        rprint(f"[green]Created [{len(file_list)}/{len(file_list)}] visualizations without saving![/green]")
    elif len(file_list) >= 1:
        rprint(f"[yellow]Created [{success}/{len(file_list)}] visualizations![/yellow]")

if __name__ == "__main__":
    main()
