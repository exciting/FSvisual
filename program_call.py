from main import main
import os

dirpath = "C:/Users/janst/OneDrive/Uni/Bachelorarbeit/Python_files/whole_program/surface_file/Al"
save_fermisurf_path = "C:/Users/janst/OneDrive/Uni/Bachelorarbeit/Python_files/whole_program/surface_file/Al"

for filename in os.listdir(dirpath):
    filepath = os.path.join(dirpath, filename)
    # check if path leads to file
    if not os.path.isfile(filepath):
        continue
    main(filepath, save_fermisurf_path)

