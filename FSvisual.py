from main import main
import os
import argparse

#dirpath = "/home/Jan/Documents/Fermisurafces/Al"
#save_fermisurf_path = "/home/Jan/Documents/Fermisurafces/Al"

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--bxsf_files_directory", help="directory (folder) where the .bxsf files (Fermi"
                                                         "surface files) are stored")
parser.add_argument("-s", "--save_fermisurfaces", help="directory where visualized Fermi surfaces "
                                                       "are stored")
args = parser.parse_args()

for filename in os.listdir(args.bxsf_files_directory):
    filepath = os.path.join(args.bxsf_files_directory, filename)
    # check if path leads to file
    if not os.path.isfile(filepath):
        continue
    main(filepath, args.save_fermisurfaces)

