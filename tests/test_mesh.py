import pytest
import numpy as np

from fsvisual.mesh import (create_cartesian_mesh, triangulate_faces, abs_vect,
                           triangle_area, triangle_center, face_center_BZ)


meshes = np.load("tests/data/mesh_algorithms/cartesian_meshes.npz")
calculated_mesh1 = create_cartesian_mesh([40, 40, 40])
calculated_mesh2 = create_cartesian_mesh([30, 30, 10])
calculated_mesh3 = create_cartesian_mesh([10, 20, 30])

@pytest.fixture
def bz_faces():
    bz_output = np.load("tests/data/brillouin_zone/bz_output/output0.npz")
    faces = [getattr(bz_output.f, f"arr_{i}") for i in range(len(bz_output))]
    return faces

@pytest.mark.parametrize("calculated_mesh, expected_mesh", [
    (calculated_mesh1, meshes.f.mesh1),
    (calculated_mesh2, meshes.f.mesh2),
    (calculated_mesh3, meshes.f.mesh3)
])

def test_mesh_calculation(calculated_mesh, expected_mesh):
    assert np.allclose(calculated_mesh, expected_mesh)

def test_triangulate_faces(bz_faces):
    expected_triangulated_faces = np.load("tests/data/mesh_algorithms/output_triangulate_faces.npz")
    bz_faces.append(np.array([[0,1,1], [0,0,2], [0,3,3]]))  # to get 100% testing coverage
    bz_faces.append(np.array([[0, 1, 1], [0, 0, 2], [0, 3, 3], [5,4,3]]))
    calculated_triangle_faces = np.array(triangulate_faces(bz_faces))
    assert np.allclose(calculated_triangle_faces, expected_triangulated_faces.f.faces)

def test_abs_vect():
    test_vector = [2.5, 10.5, 4.7]
    calculated_absolute_value = abs_vect(test_vector)
    expected_absolute_value = 11.772425408555367
    assert np.allclose(calculated_absolute_value, expected_absolute_value)

def test_triangle_area():
    test_triangle = [[2.5, 10.5, 4.7], [10, 1.6, -20], [-10.2, 8.9, 3]]
    calculated_triangle_area = triangle_area(test_triangle)
    expected_triangle_area = 175.207339030076
    assert np.allclose(calculated_triangle_area, expected_triangle_area)

def test_triangle_center():
    test_triangle = [[2.5, 55.2, 4.7], [12, 1.6, -20], [-10.2, 8.9, 3]]
    calculated_triangle_center = triangle_center(test_triangle)
    expected_triangle_center = [1.4333333333333336, 21.9, -4.1]
    assert np.allclose(calculated_triangle_center, expected_triangle_center)

def test_face_center_BZ(bz_faces):
    calculated_face_center_BZ = face_center_BZ(bz_faces)
    expected_face_center_BZ = np.load("tests/data/mesh_algorithms/output_face_centers_bz.npz")
    assert np.allclose(calculated_face_center_BZ, expected_face_center_BZ.f.face_centers)
