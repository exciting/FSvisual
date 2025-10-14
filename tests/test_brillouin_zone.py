from fsvisual.brillouin_zone import first_bz
import pytest
import numpy as np


reciprocal_basis_examples = np.load("tests/data/brillouin_zone/reciprocal_basis_examples.npz")

# standard bz data
expected_bz_output = [np.load("tests/data/brillouin_zone/bz_output/output0.npz", allow_pickle=True),
                      np.load("tests/data/brillouin_zone/bz_output/output1.npz", allow_pickle=True),
                      np.load("tests/data/brillouin_zone/bz_output/output2.npz", allow_pickle=True),
                      np.load("tests/data/brillouin_zone/bz_output/output3.npz", allow_pickle=True)]


# xyz

expected_bz_output_xyz = np.load("tests/data/brillouin_zone/bz_output_xyz.npz", allow_pickle=True)



@pytest.mark.parametrize("reciprocal_basis, expected_vertices_xyz, expected_vertices", [
    (reciprocal_basis_examples.f.basis1, expected_bz_output_xyz.f.output1, expected_bz_output[0].f),
    (reciprocal_basis_examples.f.basis2, expected_bz_output_xyz.f.output2, expected_bz_output[1].f),
    (reciprocal_basis_examples.f.basis3, expected_bz_output_xyz.f.output3, expected_bz_output[2].f),
    (reciprocal_basis_examples.f.basis4, expected_bz_output_xyz.f.output4, expected_bz_output[3].f),
])

def test_first_bz(reciprocal_basis, expected_vertices_xyz, expected_vertices):
    output_xyz = first_bz(reciprocal_basis)

    # standard part
    comparison_list = []
    for i in range(output_xyz[1]):
        comparison_list.append(np.array(output_xyz[0][i]))

    assert np.allclose(comparison_list, expected_vertices)

    # xyz part

    for j in range(len(output_xyz[0])):
        for k in range(len(output_xyz[0][j])):
            if output_xyz[0][j][k] is None:
                output_xyz[0][j][k] = np.nan

    assert np.allclose(output_xyz[0], expected_vertices_xyz, equal_nan=True), "xyz output of the Brillouin Zone vertices and facets is not as expected!"