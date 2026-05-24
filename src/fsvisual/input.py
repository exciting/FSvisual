import pandas as pd



# Define a function to process the text file
def read_energy_numbers(filepath, progress = "not_set", task = "not_set",
                                      timings = "not_set"):
    """
    function that extracts all necessary data out of the FERMISURF.bxsf file
    :param filepath: path of the FERMISURF.bxsf file
    :return: energy DataFrame, fermi energy, reciprocal base vectors, grid size
    """

    progress_tracking = (progress != "not_set" and task != "not_set" and timings != "not_set")

    if progress_tracking:
        import os
        file_size = os.path.getsize(filepath)
        lines_estimate = 0

    with open(filepath, 'r') as file:

        if progress_tracking: progress.update(task, advance=timings[0])


        # Filter out the lines containing energy numbers

        values_in_series = []
        my_dict = {}
        fermi_energy = 0
        rez_base_vect = []
        grid_size = []
        j = 0

        for i in range(14):
            line = file.readline()
            if i == 3:  # fermi_energy
                fermi_energy = float(line[19:31])
            if i == 9:  # grid_size
                grid = line.split(" ")
                grid = [int(num) for num in grid if num != "" and num != "\n"]
                grid_size.append(grid)

            if 10 < i < 14:  # base vectors
                vect = [line.split(" ")]
                vect[0] = [float(num) for num in vect[0] if num != "" and num != "\n"]
                rez_base_vect.extend(vect)


        for i, line in enumerate(file):
            if line.startswith(" BAND"):
                if j == 0:
                    pass
                else:
                    my_dict[f"Band {j}"] = values_in_series
                    values_in_series = []
                j += 1
            else:
                try:
                    values_in_series.append(float(line.strip()))
                except ValueError:
                    pass  # Ignore lines that cannot be converted to float
            if progress_tracking and i % 200000 == 0:
                if lines_estimate == 0:
                    bytes_per_line = len(line.encode("utf-8"))
                    lines_estimate = file_size / bytes_per_line

                progress.update(task, advance=timings[1]/(lines_estimate/200000))

        my_dict[f"Band {j}"] = values_in_series
        df = pd.DataFrame(my_dict)

    return df, fermi_energy, rez_base_vect, grid_size[0]
