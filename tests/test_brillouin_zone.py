from fsvisual.brillouin_zone import first_bz
import pytest
import numpy as np


reciprocal_basis_examples = np.load("tests/data/brillouin_zone/reciprocal_basis_examples.npz")

# standard bz data
expected_bz_output = [np.load("tests/data/brillouin_zone/bz_output/output0.npz"),
                      np.load("tests/data/brillouin_zone/bz_output/output1.npz"),
                      np.load("tests/data/brillouin_zone/bz_output/output2.npz")]


# xyz

expected_bz_output_xyz = np.load("tests/data/brillouin_zone/bz_output_xyz.npz")



@pytest.mark.parametrize("reciprocal_basis, expected_vertices_xyz, expected_vertices", [
    (reciprocal_basis_examples.f.basis1, expected_bz_output_xyz.f.output1, expected_bz_output[0].f),
    (reciprocal_basis_examples.f.basis2, expected_bz_output_xyz.f.output2, expected_bz_output[1].f),
    (reciprocal_basis_examples.f.basis3, expected_bz_output_xyz.f.output3, expected_bz_output[2].f),
])


def test_first_bz(reciprocal_basis, expected_vertices_xyz, expected_vertices):
    output = first_bz(reciprocal_basis)

    # standard part
    for i in range(len(output[1])):
        assert np.allclose(np.array(output[1][i]), getattr(expected_vertices, f"arr_{i}")), "Standard output of the Brillouin Zones vertices and facets is not as expected!"

    # xyz part
    for j in range(len(output[0])):
        for k in range(len(output[0][j])):
            if output[0][j][k] is None:
                output[0][j][k] = np.nan

    assert np.allclose(output[0], expected_vertices_xyz, equal_nan=True), "XYZ output of the Brillouin Zones vertices and facets is not as expected!"