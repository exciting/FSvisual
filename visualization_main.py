import plotly.graph_objects as go
from brilouin_zone import first_bz
from fermi_surfaces import create_mol_mesh, brillouin_intersect_mesh, facet_plane, create_basevect_mesh, face_center_BZ
from input import read_energy_numbers
import numpy as np
import trimesh
from scipy.spatial import Delaunay
import plotly.offline as pyo
import pandas as pd

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

# create 3d object of the first BZ
mew_brillouin_zone_object = brillouin_intersect_mesh(brillouin_zone[1])
# translation of the first BZ cause the bascevect_mesh starts at [0,0,0]
#mew_brillouin_zone_object.apply_translation([np.abs(rez_base_vect[0][0]), np.abs(rez_base_vect[0][0]), np.abs(rez_base_vect[0][0])])

#mew_brillouin_zone_object.show()
# create mol mesh and basevect_mesh

new_mols = create_mol_mesh(rez_base_vect, grid_size, brillouin_zone)
new_basevect_mesh = create_basevect_mesh(rez_base_vect, grid_size)

test = brillouin_zone[1][0]

mc_energy_values_list = []
new_mols_helper = []

from copy import deepcopy

for columnName in energy.columns:
    if columnName == "Band 4":
        placeholder_energy = []
        new_mols_helper = deepcopy(new_mols["molgrid"])
        # absolute value of lattice vectors
        abs_vec = [np.sqrt(rez_base_vect[0][0]**2 + rez_base_vect[0][1]**2 + rez_base_vect[0][2]**2),
                   np.sqrt(rez_base_vect[1][0]**2 + rez_base_vect[1][1]**2 + rez_base_vect[1][2]**2),
                   np.sqrt(rez_base_vect[2][0]**2 + rez_base_vect[2][1]**2 + rez_base_vect[2][2]**2)]

        for i in range(81):
            for k in range(81):
                for j in range(81):
                    new_mols_helper[i][j][k] = energy[columnName][int(new_mols["molgrid"][i][j][k])]


    # energy[columnName] = placeholder_energy
    print("done")
    mc_energy_values_list.append(new_mols_helper)

from skimage import measure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# energy_values = np.random.random((grid_size, grid_size, grid_size))  # Replace with your actual energy values
grid_size = 81
# Define the isovalue for the surface (this value should represent the energy level that forms the surface)
isovalue = 0.0  # Adjust this value based on your data

# Apply the Marching Cubes algorithm
vertices, faces, normals, values = measure.marching_cubes(new_mols_helper, level=isovalue)
# vertices, faces = marching_cubes_clip(rez_base_vect, faces, vertices, mew_brillouin_zone_object, grid_size)

test_vertices = deepcopy(vertices)

for i, vertex in enumerate(test_vertices):
    p = int(round(vertex[2])) + int(round(vertex[1])*grid_size) + int(round(vertex[0])*grid_size**2)
    test_vertices[i] = new_basevect_mesh[p]

new_vertices = []
clipped_vertices = []
for i, vertex in enumerate(test_vertices):
    new_vertices.append(vertex)
    vertex = [vertex[0]*2-np.abs(rez_base_vect[0][0]),  # why is that?
              vertex[1]*2-np.abs(rez_base_vect[0][0]), vertex[2]*2-np.abs(rez_base_vect[0][0])]
    test_vertices[i] = vertex


x_f = [value[0] for value in new_vertices]
y_f = [value[1] for value in new_vertices]
z_f = [value[2] for value in new_vertices]

# Visualization
# visualization of the brillouin_zone

fermi_surface = trimesh.Trimesh(vertices=test_vertices, faces=faces, process=False)
"""
remove_indices = clipped_vertices

# Mark vertices for removal by setting them to None
mask = np.ones(len(fermi_surface.vertices), dtype=bool)
mask[remove_indices] = False

# Create a new mesh with only the vertices and faces that are needed
fermi_surface.update_vertices(mask)

# Clean up unreferenced vertices
fermi_surface.remove_unreferenced_vertices()

fermi_surface = fermi_surface.smooth_shaded
"""
# len(brillouin_zone[1])
facet_centers = face_center_BZ(brillouin_zone[1])
for i in range(len(brillouin_zone[1])):
    facets_normal = np.array(facet_centers[i]) + 1/2 * np.array(facet_centers[i])

    positive_fermisurface = fermi_surface.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                    plane_normal=facets_normal)
    negative_fermisurface = fermi_surface.slice_plane(plane_origin=brillouin_zone[1][i][0],
                                                    plane_normal=facets_normal * (-1))

    if len(positive_fermisurface.vertices) > len(negative_fermisurface.vertices):
        fermi_surface = positive_fermisurface
    else:
        fermi_surface = negative_fermisurface



    #new_center_plane = 2*face_center(brillouin_zone[1][2])
    #fermi_surface = fermi_surface.slice_plane(plane_origin=mew_brillouin_zone_object.facets_origin[3], plane_normal=test_array)

test_list = []
for num in mew_brillouin_zone_object.facets_normal:
    test_list.append(num)
for num in mew_brillouin_zone_object.facets_origin:
    test_list.append(num)


x_f = [value[0] for value in test_triangle]
y_f = [value[1] for value in test_triangle]
z_f = [value[2] for value in test_triangle]

x_mesh, y_mesh, z_mesh = fermi_surface.vertices[:, 0], fermi_surface.vertices[:, 1], fermi_surface.vertices[:, 2]
#x_mesh, y_mesh, z_mesh = test_vertices[:, 0], test_vertices[:, 1], test_vertices[:, 2]

# Extract I, J, K indices of faces
i, j, k = fermi_surface.faces[:, 0], fermi_surface.faces[:, 1], fermi_surface.faces[:, 2]
#i, j, k = faces[:, 0], faces[:, 1], faces[:, 2]

mesh_fermi_surface = go.Mesh3d(
    x=np.array(x_mesh),
    y=np.array(y_mesh),
    z=np.array(z_mesh),
    i=np.array(i),
    j=np.array(j),
    k=np.array(k),
    color='lightblue',
    opacity=1
)
mesh_fermi_surface_inside = go.Mesh3d(
    x=np.array(x_mesh)*0.99,
    y=np.array(y_mesh)*0.99,
    z=np.array(z_mesh)*0.99,
    i=np.array(i),
    j=np.array(j),
    k=np.array(k),
    color='red',
    opacity=0.6
)


scatter_fermi_surface = go.Scatter3d(
    x=x_f,
    y=y_f,
    z=z_f,
    mode='markers',
    marker=dict(
        size=5,
        color=z_f,                # Set color to the z values
        colorscale='Viridis',   # Choose a colorscale
        opacity=0.8
    )
)

# Create a 3D scatter plot
scatter_BZ = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='lines',
    line=dict(color='black', width=2)
)

# contains all
fig_data = [scatter_BZ, mesh_fermi_surface, scatter_fermi_surface]



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



"""
#print(faces)
# Plot the resulting surface
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Create a Poly3DCollection from the vertices and faces
mesh = Poly3DCollection(test_vertices[faces], alpha=0.7)
mesh.set_facecolor('cyan')
mesh.set_edgecolor('k')
ax.add_collection3d(mesh)

# Set plot limits

ax.set_xlim(0, 81)
ax.set_ylim(0, 81)
ax.set_zlim(0, 81)

plt.show()
"""