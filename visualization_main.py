import plotly.graph_objects as go
from brilouin_zone import first_bz
from fermi_surfaces import create_mol_mesh, create_basevect_mesh, face_center_BZ
from input import read_energy_numbers
import numpy as np
import trimesh
from skimage import measure
import pandas as pd

source = "FS-Au-PBEsol.bxsf"
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
new_basevect_grid_size = [grid_size[0]*2-1, grid_size[1]*2-1, grid_size[2]*2-1]
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

    # Visualization
    # visualization of the brillouin_zone

    fermi_surface = trimesh.Trimesh(vertices=new_vertices, faces=faces, process=False)

    # len(brillouin_zone[1])
    facet_centers = face_center_BZ(brillouin_zone[1])

    # cutting off the surface area outside the 1. BZ
    for i in range(len(brillouin_zone[1])):
        facets_normal = np.array(facet_centers[i]) + 1 / 2 * np.array(facet_centers[i])

        fermi_surface = fermi_surface.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                  plane_normal=facets_normal * (-1))

    fermi_surface = fermi_surface.smooth_shaded
    fermi_surface_list.append(fermi_surface)

x_f = [value[0] for value in test_triangle]
y_f = [value[1] for value in test_triangle]
z_f = [value[2] for value in test_triangle]

mesh_fermi_surfaces = []
for index, fermi_surface in enumerate(fermi_surface_list):
    x_mesh, y_mesh, z_mesh = fermi_surface.vertices[:, 0], fermi_surface.vertices[:, 1], fermi_surface.vertices[:, 2]

    # Extract I, J, K indices of faces
    i, j, k = fermi_surface.faces[:, 0], fermi_surface.faces[:, 1], fermi_surface.faces[:, 2]

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
