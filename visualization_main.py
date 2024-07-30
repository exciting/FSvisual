from brilouin_zone import first_bz
from fermi_surfaces import create_mol_mesh, create_basevect_mesh, face_center_BZ
import plotly.graph_objects as go
from input import read_energy_numbers
import numpy as np
import trimesh
from skimage import measure
import open3d as o3d
import pandas as pd
import pymeshlab

source = "FERMISURF_Au_fcc.bxsf"
data = read_energy_numbers(source)
energy = data[0]
fermi_energy = data[1]
rez_base_vect = data[2]
grid_size = data[3]

# coordinates of the first Brillouin zone

brillouin_zone = []
brillouin_zone.extend(first_bz(rez_base_vect))
x = brillouin_zone[0][0]
y = brillouin_zone[0][1]
z = brillouin_zone[0][2]

# test for triangle centers
test_triangle = face_center_BZ(brillouin_zone[1])

new_mols = create_mol_mesh(grid_size)
new_basevect_mesh = create_basevect_mesh(rez_base_vect, grid_size)
new_basevect_grid_size = np.array([grid_size[0]*2-1, grid_size[1]*2-1, grid_size[2]*2-1])
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

    band_index.append(index+1)
    new_vertices = deepcopy(vertices)

    # transform vertices, so it fits the base_vect_grid
    for i, vertex in enumerate(new_vertices):
        p = int(round(vertex[2])) + int(round(vertex[1]) * new_basevect_grid_size[1]) + int(round(vertex[0]) * new_basevect_grid_size[0] ** 2)
        new_vertices[i] = new_basevect_mesh[p]

    for i, vertex in enumerate(new_vertices):
        vertex = [vertex[0] * 2 - np.abs(rez_base_vect[0][0]),  # why is that?
                  vertex[1] * 2 - np.abs(rez_base_vect[0][0]), vertex[2] * 2 - np.abs(rez_base_vect[0][0])]
        new_vertices[i] = vertex

    test = np.dot(vertices, np.array(rez_base_vect))

    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(test, faces))

    # Wende anisotrope Diffusionsglättung an
    ms.meshing_surface_subdivision_loop(iterations=3)
    ms.apply_coord_laplacian_smoothing_scale_dependent(stepsmoothnum=3)  # Beispiel-Filter für anisotrope Diffusion

    # Extrahiere geglättetes Mesh
    smoothed_mesh = ms.current_mesh()
    smoothed_vertices = np.asarray(smoothed_mesh.vertex_matrix())
    smoothed_facets = np.asarray(smoothed_mesh.face_matrix())

    # test

    test_mesh = trimesh.Trimesh(vertices=np.asarray(smoothed_mesh.vertex_matrix()), faces=np.asarray(smoothed_mesh.face_matrix()), process=False)
    # tranlatation and shrincage einfügen

    from pymatgen.core import Lattice

    reciprocal_lattice = Lattice(rez_base_vect)

    # Umwandlung in das direkte Gitter
    direct_lattice = reciprocal_lattice.reciprocal_lattice.matrix

    scale_factors = 2/new_basevect_grid_size  # 2 wegen Durschmesser 1. BZ  # nochmal gucken. passt nicht ganz

    # Create a scaling matrix
    scaling_matrix = np.eye(4)
    scaling_matrix[:3, :3] *= scale_factors

    # Apply the scaling transformation to the mesh
    test_mesh.apply_transform(scaling_matrix)

    #translation
    test_mesh.apply_translation([-test_mesh.centroid[0], -test_mesh.centroid[1], -test_mesh.centroid[2]])

    facet_centers = face_center_BZ(brillouin_zone[1])

    # cutting off the surface area outside the 1. BZ
    for i in range(len(brillouin_zone[1])):
        facets_normal = np.array(facet_centers[i]) + 1 / 2 * np.array(facet_centers[i])

        test_mesh = test_mesh.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                  plane_normal=facets_normal * (-1))

    x_mesh, y_mesh, z_mesh = test_mesh.vertices[:, 0], test_mesh.vertices[:, 1], test_mesh.vertices[:, 2]
    # x_mesh, y_mesh, z_mesh = smoothed_mesh.vertex_matrix()[:, 0], smoothed_vertices[:, 1], smoothed_vertices[:, 2]

    # Extract I, J, K indices of faces
    i, j, k = test_mesh.faces[:, 0], test_mesh.faces[:, 1], test_mesh.faces[:, 2]
    mesh_fermi_surfaces = []
    mesh_fermi_surfaces.append(go.Mesh3d(
        x=np.array(x_mesh),
        y=np.array(y_mesh),
        z=np.array(z_mesh),
        i=np.array(i),
        j=np.array(j),
        k=np.array(k),
        # color='lightblue',
        opacity=1,
        showlegend=True
    ))
    scatter_BZ = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='lines',
        name="1. BZ",
        line=dict(color='black', width=2)
    )

    fig_data = [scatter_BZ]
    fig_data.extend(mesh_fermi_surfaces)

    fig = go.Figure(data=fig_data)

    # Define the layout of the plot
    fig.update_layout(
        scene=dict(
            xaxis_title='kx',
            yaxis_title='ky',
            zaxis_title='kz',
            aspectmode='cube'
        )
    )

    # Show the plot
    # axis ranges

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            annotations=[],  # Remove any annotations if present
            aspectmode='cube',
            camera=dict(
                projection=dict(
                    type='orthographic'
                    # to change the perspective (so that lines dont distort over distance (nicht verjüngen))
                )
            )
        )
    )

    fig.show()
    # end test

    new_triangle_mesh = o3d.geometry.TriangleMesh()
    new_triangle_mesh.vertices = o3d.utility.Vector3dVector(new_vertices)
    new_triangle_mesh.triangles = o3d.utility.Vector3iVector(faces)
    new_triangle_mesh.compute_vertex_normals()

    print(
        f'The mesh has {len(new_triangle_mesh.vertices)} vertices and {len(new_triangle_mesh.triangles)} triangles'
    )
    new_triangle_mesh = new_triangle_mesh.subdivide_loop(number_of_iterations=1)
    print(
        f'After subdivision it has {len(new_triangle_mesh.vertices)} vertices and {len(new_triangle_mesh.triangles)} triangles'
    )
    new_triangle_mesh = new_triangle_mesh.filter_smooth_taubin(number_of_iterations=10)
    new_triangle_mesh = new_triangle_mesh.subdivide_loop(number_of_iterations=1)

    #new_triangle_mesh = new_triangle_mesh.filter_smooth_laplacian(number_of_iterations=10)

    o3d.visualization.draw_geometries([new_triangle_mesh], mesh_show_wireframe=True)
    # Visualization
    # visualization of the brillouin_zone

    fermi_surface = trimesh.Trimesh(vertices=np.asarray(new_triangle_mesh.vertices), faces=np.asarray(new_triangle_mesh.triangles), process=False)

    # len(brillouin_zone[1])
    facet_centers = face_center_BZ(brillouin_zone[1])

    # cutting off the surface area outside the 1. BZ
    for i in range(len(brillouin_zone[1])):
        facets_normal = np.array(facet_centers[i]) + 1 / 2 * np.array(facet_centers[i])

        fermi_surface = fermi_surface.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                  plane_normal=facets_normal * (-1))

    fermi_surface_list.append(fermi_surface)



x_f = [value[0] for value in test_triangle]
y_f = [value[1] for value in test_triangle]
z_f = [value[2] for value in test_triangle]

mesh_fermi_surfaces = []
for index, fermi_surface in enumerate(fermi_surface_list):

    x_mesh, y_mesh, z_mesh = fermi_surface.vertices[:, 0], fermi_surface.vertices[:, 1], fermi_surface.vertices[:, 2]
    #x_mesh, y_mesh, z_mesh = smoothed_mesh.vertex_matrix()[:, 0], smoothed_vertices[:, 1], smoothed_vertices[:, 2]

    # Extract I, J, K indices of faces
    i, j, k = fermi_surface.faces[:, 0], fermi_surface.faces[:, 1], fermi_surface.faces[:, 2]
    #i, j, k = smoothed_faces[:, 0], smoothed_faces[:, 1], smoothed_faces[:, 2]

    mesh_fermi_surfaces.append(go.Mesh3d(
        x=np.array(x_mesh),
        y=np.array(y_mesh),
        z=np.array(z_mesh),
        i=np.array(i),
        j=np.array(j),
        k=np.array(k),
        name=f"Band {band_index[index]}",
        #color='lightblue',
        opacity=1,
        showlegend = True
    ))

scatter_fermi_surface = go.Scatter3d(
    x=x_f,
    y=y_f,
    z=z_f,
    name="facet center points",
    mode='markers',
    marker=dict(
        size=5,
        color=z_f,  # Set color to the z values
        colorscale='Viridis',  # Choose a colorscale
        opacity=0.8
    )
)

# Create a 3D scatter plot
scatter_BZ = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='lines',
    name="1. BZ",
    line=dict(color='black', width=2)
)

# contains all
fig_data = [scatter_BZ, scatter_fermi_surface]
fig_data.extend(mesh_fermi_surfaces)

fig = go.Figure(data=fig_data)

# Define the layout of the plot
fig.update_layout(
    scene=dict(
        xaxis_title='kx',
        yaxis_title='ky',
        zaxis_title='kz',
        aspectmode='cube'
    )
)

# Show the plot
# axis ranges


fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        annotations=[],  # Remove any annotations if present
        aspectmode='cube',
        camera=dict(
            projection=dict(
                type='orthographic'
                # to change the perspective (so that lines dont distort over distance (nicht verjüngen))
            )
        )
    )
)

fig.show()
