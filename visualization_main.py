import plotly.graph_objects as go
from brilouin_zone import first_bz
from fermi_surfaces import create_mesh, brillouin_intersect_mesh, marching_cubes_clip, check_fermi_surface
from input import read_energy_numbers
import numpy as np
from scipy.spatial import Delaunay
import plotly.offline as pyo
import pandas as pd

source = "FERMISURF_Po_sc.bxsf"
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

# create 3d object of the first BZ
mew_brillouin_zone_object = brillouin_intersect_mesh(brillouin_zone[1])

# big BZ:
new_rez_base_vect = np.array(rez_base_vect)
new_rez_base_vect[0] *= 35
new_rez_base_vect[1] *= 35
new_rez_base_vect[2] *= 35
big_bz = []
big_bz.extend(first_bz(new_rez_base_vect))
print(big_bz[0][0])
for i, vertex_lists in enumerate(big_bz[1]):
    for j, vertex_list in enumerate(vertex_lists):
        big_bz[1][i][j] += 0



new_big_bz_object = brillouin_intersect_mesh(big_bz[1])
new_big_bz_object.apply_translation([40,40,40])

# create standard mesh

all_meshs = create_mesh(rez_base_vect, grid_size, brillouin_zone)
new_mesh = all_meshs[0]  # mesh that refers to real 1. BZ
new_mols = all_meshs[1]
mc_energy_values_list = []
new_mols_helper = []

from copy import deepcopy

for columnName in energy.columns:
    if columnName == "Band 4":
        placeholder_energy = []
        new_mols_helper = deepcopy(new_mols["molgrid"])
        p = 0
        for i in range(81):
            for k in range(81):
                for j in range(81):
                    # energy_list = energy[columnName].tolist()
                    #placeholder_energy.append(energy[columnName][int(new_mols["molgrid"][i][j][k])])

                    #if fermi_energy - 0.01 <= energy[columnName][int(new_mols["molgrid"][i][j][k])] <= fermi_energy + 0.01:
                    if False:
                        if p >= grid_size[0]*grid_size[1]*grid_size[1]:
                            p = 0
                        if new_big_bz_object.contains([[i, j, k]]):
                            new_mols_helper[i][j][k] = energy[columnName][int(new_mols["molgrid"][i][j][k])]
                        else:
                            new_mols_helper[i][j][k] = 10

                    else:
                        new_mols_helper[i][j][k] = energy[columnName][int(new_mols["molgrid"][i][j][k])]
                    p += 1

    # energy[columnName] = placeholder_energy
    print("done")
    mc_energy_values_list.append(new_mols_helper)
# extract all k_points at fermi_energy
# iterate through energy bands:

k_points_dict = {}
for (columnName, columnData) in energy.items():
    k_point_indices = check_fermi_surface(columnData, fermi_energy)
    k_points_list = [new_mesh[index].tolist() for index in k_point_indices]  # list of k_points for each band
    k_points_dict[columnName] = k_points_list

# calculate intersections


scatter_fermi = []
surface_bands = []
for key, value in k_points_dict.items():
    point_index = []
    for point in range(len(value)):
        k_points_dict[key][point][0] += -rez_base_vect[0][0] / 2
        k_points_dict[key][point][1] += -rez_base_vect[0][0] / 2
        k_points_dict[key][point][2] += -rez_base_vect[0][0] / 2

        if mew_brillouin_zone_object.contains([value[point]])[0]:
            pass
        else:
            # removes point outside 1. bz (for now)
            # print(k_points_dict[key])
            point_index.append(value[point])

    # for index in point_index:
    # k_points_dict[key].remove(index)

    # plot of fermi_surfaces for each band

    scatter_fermi.append(go.Scatter3d(x=[value[0] for value in k_points_dict[key]],
                                      y=[value[1] for value in k_points_dict[key]],
                                      z=[value[2] for value in k_points_dict[key]],
                                      mode='markers'))
    # if len(k_points_dict[key]) != 0:

    # Sample data: replace these lists with your actual data

from scipy.interpolate import Rbf
import plotly.io as pio

"""

x = [value[0] for value in k_points_dict["Band 4"]]
y = [value[1] for value in k_points_dict["Band 4"]]
z = [value[2] for value in k_points_dict["Band 4"]]

X,Y = np.meshgrid(x,y)

# Convert spherical coordinates to Cartesian coordinates

# Create the 3D mesh plot
fig = go.Figure(data=[go.Mesh3d(
    x=X,
    y=Y,
    z=z,
    color='lightblue',
    opacity=0.50

)])

# Update the layout
fig.update_layout(
    scene=dict(
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        zaxis_title='Z Axis',
    ),
    title='Irregular Sphere 3D Mesh Plot',
    autosize=True
)

# Show the plot
fig.show()





# Visualization
# visualization of the brillouin_zone

# Create a 3D scatter plot
scatter_BZ = go.Scatter3d(
    x=x,
    y=y,
    z=z,
    mode='lines',
    line=dict(color='black', width=2)
)

# contains all
fig_data = [scatter_BZ]
fig_data.extend(scatter_fermi)

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
x_range = [-np.abs(rez_base_vect[0][0]), np.abs(rez_base_vect[0][0])]
y_range = [-np.abs(rez_base_vect[0][0]), np.abs(rez_base_vect[0][0])]
z_range = [-np.abs(rez_base_vect[0][0]), np.abs(rez_base_vect[0][0])]


fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=x_range),
        yaxis=dict(visible=False, range=y_range),
        zaxis=dict(visible=False, range=z_range),
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

import numpy as np
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

#print(faces)
# Plot the resulting surface
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Create a Poly3DCollection from the vertices and faces
mesh = Poly3DCollection(vertices[faces], alpha=0.7)
mesh.set_facecolor('cyan')
mesh.set_edgecolor('k')
ax.add_collection3d(mesh)

# Set plot limits

ax.set_xlim(0, 81 - 1)
ax.set_ylim(0, 81 - 1)
ax.set_zlim(0, 81 - 1)

"""
ax.set_xlim(0, rez_base_vect[0])
ax.set_ylim(0, rez_base_vect[0])
ax.set_zlim(0, rez_base_vect[0])
"""
plt.show()
