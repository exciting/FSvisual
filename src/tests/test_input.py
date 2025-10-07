from fsvisual.input import read_energy_numbers
import pytest
import numpy as np
import pandas as pd

input_file_1 = "/home/Jan/PycharmProjects/FSvisual/src/tests/data/bxsf/fcc_41x41x41.bxsf"
exp_energy_num_1 = np.load("/home/Jan/PycharmProjects/FSvisual/src/tests/data/npz/expected_fcc_41x41x41.npz")
exp_energy_num_1 = [exp_energy_num_1.f.df, exp_energy_num_1.f.fermi_enery, exp_energy_num_1.f.rez_base_vect,
                    exp_energy_num_1.f.grid_size]

@pytest.mark.parametrize("input_file, expected_energy_numbers", [
    (input_file_1, exp_energy_num_1) # fcc, 41x41x41
])

def test_read_energy_numbers(input_file, expected_energy_numbers):
    read = read_energy_numbers(input_file)
    num_bands = 7
    columns = [f"Band {i+1}" for i in range(num_bands)]
    exp_energy_num_1[0] = pd.DataFrame(expected_energy_numbers[0], columns=columns)
    expected_energy_numbers[2] = exp_energy_num_1[2].tolist()

    assert read[0].equals(expected_energy_numbers[0]), "dataframe is not read correctly"
    assert read[1] == expected_energy_numbers[1], "fermi energy is not read correctly"
    assert read[2] == expected_energy_numbers[2], "reciprocal base vectors are not read correctly"
    assert read[3] == expected_energy_numbers[3], "grid size is not read correctly"