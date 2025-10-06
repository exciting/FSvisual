from fsvisual.input import read_energy_numbers
import pytest

@pytest.mark.parametrize("input_file, expected_energy_numbers", [
    ("filepath", data)
])

def test_read_energy_numbers(input_file, expected_energy_numbers):
    assert read_energy_numbers(input_file) == expected_energy_numbers, "file is not read correctly"