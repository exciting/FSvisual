from main import main
import os

dirpath = "E:/Fermisurfaces/GGA"
save_fermisurf_path = "E:/Fermisurfaces/finished_plots"

for filename in os.listdir(dirpath):
    filepath = os.path.join(dirpath, filename)
    # check if path leads to file
    if not os.path.isfile(filepath):
        continue
    main(filepath, save_fermisurf_path)

