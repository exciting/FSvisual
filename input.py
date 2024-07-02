import pandas as pd


# Define a function to process the text file
def read_energy_numbers(filepath):
    """
    function that extracts all necessary data out of the FERMISURF.bxsf file
    :param filepath: path of the FERMISURF.bxsf file
    :return: energy DataFrame, fermi energy, reciprocal base vectors, grid size
    """

    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Filter out the lines containing energy numbers

    values_in_series = []
    my_dict = {}
    fermi_energy = 0
    rez_base_vect = []
    grid_size = []
    j = 0
    for i, line in enumerate(lines):
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
        if i >= 13:  # algorythm that collects all the energies and stores them into separate bands
            if line.startswith(" BAND"):
                if j == 0:
                    pass
                else:
                    my_dict[f"Band {j}"] = values_in_series
                    values_in_series = []
                j += 1
            try:
                energy = float(line.strip())
                values_in_series.append(energy)
            except ValueError:
                pass  # Ignore lines that cannot be converted to float

        i += 1
    my_dict[f"Band {j}"] = values_in_series
    df = pd.DataFrame(my_dict)
    return df, fermi_energy, rez_base_vect, grid_size[0]
