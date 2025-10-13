from fsvisual.brillouin_zone import first_bz
import pytest
import numpy as np

reciprocal_basis_examples = np.load("src/tests/data/brillouin_zone/reciprocal_basis_examples.npz")
expected_bz_output_xyz = np.load("src/tests/data/brillouin_zone/bz_output_xyz.npz")

@pytest.mark.parametrize("reciprocal_basis, expected_vertices_xyz, expected_vertices", [
    (reciprocal_basis_examples.f.basis1, expected_bz_output_xyz.f.output1, expected_bz_output_xyz[0]),
])

def test_first_bz(reciprocal_basis, expected_vertices_xyz, expected_vertices):
    output_xyz = first_bz(reciprocal_basis)
    assert np.allclose(output_xyz[0], expected_vertices_xyz)