import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os


def plot(fermi_surface_list, brillouin_zone_object, band_index, filepath, save_fermisurf_path):
    mesh_fermi_surfaces = []
    for index, fermi_surface in enumerate(fermi_surface_list):
        x_mesh, y_mesh, z_mesh = fermi_surface.vertices[:, 0], fermi_surface.vertices[:, 1], fermi_surface.vertices[:,
                                                                                             2]
        # x_mesh, y_mesh, z_mesh = smoothed_mesh.vertex_matrix()[:, 0], smoothed_vertices[:, 1], smoothed_vertices[:, 2]

        # Extract I, J, K indices of faces
        i, j, k = fermi_surface.faces[:, 0], fermi_surface.faces[:, 1], fermi_surface.faces[:, 2]
        # i, j, k = smoothed_faces[:, 0], smoothed_faces[:, 1], smoothed_faces[:, 2]

        mesh_fermi_surfaces.append(go.Mesh3d(
            x=np.array(x_mesh),
            y=np.array(y_mesh),
            z=np.array(z_mesh),
            i=np.array(i),
            j=np.array(j),
            k=np.array(k),
            name=f"Band {band_index[index]}",
            # color='lightblue',
            opacity=1,
            showlegend=True
        ))

    x = brillouin_zone_object[0][0]
    y = brillouin_zone_object[0][1]
    z = brillouin_zone_object[0][2]

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

    #fig.show()
    filename = os.path.basename(filepath)
    filename = filename.split(".")[0]
    pio.write_html(fig, file=f'{save_fermisurf_path}/{filename}.html', auto_open=False, config={'displayModeBar': False})

    fig.update_layout(
        showlegend=False,
        scene_camera=dict(eye=dict(x=1, y=1, z=1)),  # change camera scene
        margin=dict(l=0, r=0, b=0, t=0)  # set the space on the edges to 0 (so that the plot fills out the image)
    )
    #fig.write_image(f'{save_fermisurf_path}/{filename}.svg', format="svg", width=500, height=800)
