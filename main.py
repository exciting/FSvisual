from brilouin_zone import first_bz
from fermi_surfaces import create_mol_mesh, face_center_BZ
from visualisation import plot
from input import read_energy_numbers
import numpy as np
import trimesh
from skimage import measure
import pandas as pd
import pymeshlab

source = "FERMISURF_Po_sc.bxsf"
data = read_energy_numbers(source)
energy = data[0]
fermi_energy = data[1]
rez_base_vect = data[2]
grid_size = data[3]

# coordinates of the first Brillouin zone

brillouin_zone = []
brillouin_zone.extend(first_bz(rez_base_vect))

new_mols = create_mol_mesh(grid_size)
new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])
fermi_surface_list = []

from copy import deepcopy

new_mols_helper = []
band_index = []
for index, columnName in enumerate(energy.columns):
    placeholder_energy = []
    new_mols_helper = deepcopy(new_mols["molgrid"])

    for i in range(new_basevect_grid_size[0]):
        for k in range(new_basevect_grid_size[1]):
            for j in range(new_basevect_grid_size[2]):
                new_mols_helper[i][j][k] = energy[columnName][int(new_mols["molgrid"][i][j][k])]

    # energy[columnName] = placeholder_energy
    print("done")

    # Define the isovalue for the surface (this value represents the energy level that forms the surface)
    isovalue = 0.0

    # Apply the Marching Cubes algorithm
    try:
        vertices, faces, normals, values = measure.marching_cubes(new_mols_helper, level=isovalue)
    except ValueError:
        "nothing here"
        continue

    band_index.append(index + 1)  # for the plot
    new_vertices = deepcopy(vertices)

    # transform vertices, so it fits the base_vect_grid

    test = np.dot(vertices, np.array(rez_base_vect))

    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(test, faces))

    ms.meshing_surface_subdivision_loop(iterations=3)
    ms.apply_coord_laplacian_smoothing_scale_dependent(stepsmoothnum=3)  # Beispiel-Filter für anisotrope Diffusion

    smoothed_mesh = ms.current_mesh()
    smoothed_vertices = np.asarray(smoothed_mesh.vertex_matrix())
    smoothed_facets = np.asarray(smoothed_mesh.face_matrix())

    fermi_surface = trimesh.Trimesh(vertices=np.asarray(smoothed_mesh.vertex_matrix()),
                                    faces=np.asarray(smoothed_mesh.face_matrix()), process=False)

    # translation and shrinkage

    scale_factors = 2 / new_basevect_grid_size  # 2 wegen Durchmesser 1. BZ  # nochmal gucken.

    # Create a scaling matrix
    scaling_matrix = np.eye(4)
    scaling_matrix[:3, :3] *= scale_factors

    # Apply the scaling transformation to the mesh
    fermi_surface.apply_transform(scaling_matrix)

    # translation

    fermi_surface.apply_translation(
        [-fermi_surface.centroid[0], -fermi_surface.centroid[1], -fermi_surface.centroid[2]])

    facet_centers = face_center_BZ(brillouin_zone[1])

    # cutting off the surface area outside the 1. BZ
    for i in range(len(brillouin_zone[1])):
        facets_normal = np.array(facet_centers[i]) + 1 / 2 * np.array(facet_centers[i])

        fermi_surface = fermi_surface.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                  plane_normal=facets_normal * (-1))

    fermi_surface_list.append(fermi_surface)

# visualization
plot(fermi_surface_list, brillouin_zone, band_index)
