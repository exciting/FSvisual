import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
import os
import kaleido


def build_plotly_figure(fermi_surface_list, brillouin_zone_object, band_index):
    """
    to build the Fermi surface as a 3D interactive plotly figure
    :param fermi_surface_list: list of all surface parts of the Fermi surface
    :param brillouin_zone_object: the brillouin zone object created with the compute_brillouin_zone from FSvisual
    :param band_index: list of band indices corresponding to each surface part
    :return: the plotly figure
    """
    mesh_fermi_surfaces = []
    for index, fermi_surface in enumerate(fermi_surface_list):
        x_mesh, y_mesh, z_mesh = fermi_surface.vertices[:, 0], fermi_surface.vertices[:, 1], fermi_surface.vertices[:,
                                                                                             2]

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
            opacity=1,
            showlegend=True
        ))

    x = brillouin_zone_object[0][0]
    y = brillouin_zone_object[0][1]
    z = brillouin_zone_object[0][2]

    # find highest and lowest point of BZ for axis scaling:

    # filter non values and find maximum on each axis
    max_x = np.max([np.abs(num) for num in x if num is not None])
    max_y = np.max([np.abs(num) for num in y if num is not None])
    max_z = np.max([np.abs(num) for num in z if num is not None])

    # calculate global maximum
    max_value_axis = np.max([max_x, max_y, max_z])


    if max_value_axis > 0:
        max_value_axis += 1/10*max_value_axis
    else:
        max_value_axis -= 1/10*max_value_axis


    # Create a 3D scatter plot
    scatter_BZ = go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode='lines',
        name="1. BZ",
        line=dict(color='black', width=6)
    )

    # contains all
    fig_data = [scatter_BZ]
    fig_data.extend(mesh_fermi_surfaces)

    fig = go.Figure(data=fig_data)

    fig.update_layout(

        scene=dict(
            xaxis=dict(
                range=[-max_value_axis, max_value_axis],  # Fester Bereich für x-Achse
                visible=False
            ),
            yaxis=dict(
                range=[-max_value_axis, max_value_axis],  # Fester Bereich für y-Achse
                visible=False
            ),
            zaxis=dict(
                range=[-max_value_axis, max_value_axis],  # Fester Bereich für z-Achse
                visible=False
            ),
            annotations=[],  # Remove any annotations if present
            aspectmode='cube',
            camera=dict(
                projection=dict(
                    type='orthographic'
                    # to change the perspective (so that lines don't distort over distance)
                )
            )
        )
    )
    return fig


def write_figure_to_file(fig, filepath, save_figure_directory, create_SVG=True,
                         scene_camera_SVG=None):
    """
    Function to take a plotly figure and write it to a file with potentially also creating an SVG file.
    :param fig: plotly figure
    :param filepath: path to .bxsf file/files
    :param save_figure_directory: directory where to save the figure
    :param create_SVG: boolean whether to create SVG file
    :param scene_camera_SVG: alter the cameras position and angle with dictionary (scene_camera parameter in plotly)
    """

    filename = os.path.basename(filepath)
    filename = filename.split(".")[0]
    pio.write_html(fig, file=f'{save_figure_directory}/{filename}.html', auto_open=False,
                   config={'displayModeBar': False})

    if create_SVG:
        kaleido.get_chrome_sync()
        if scene_camera_SVG is None:
            scene_camera_SVG = dict(eye=dict(x=1, y=1, z=1))
        fig.update_layout(
            showlegend=False,
            scene_camera=scene_camera_SVG,  # change camera scene
            margin=dict(l=0, r=0, b=0, t=0)  # set the space on the edges to 0 (so that the plot fills out the image)
        )
        fig.write_image(f'{save_figure_directory}/{filename}.svg', format="svg", width=500, height=800)
