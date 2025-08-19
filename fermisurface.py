from input import read_energy_numbers
from brilouin_zone import first_bz
from visualisation import build_plotly_figure, write_figure_to_file
from mesh_algorythms import create_cartesian_mesh, scale, centering, \
    face_center_BZ, subdivision_surface, downsample_mesh
from skimage import measure
import numpy as np
import trimesh
import pymeshlab


class FermiSurface:
    """
    Class for computing three-dimensional, interactive Fermi surfaces from .bxsf files, a filetype established by the
    visualization software XCrsSDen. A Fermi surface is an object in k-space, that separates the occupied from the
    unoccupied states (at the Fermi energy). Fermi surfaces are often shown within the first brillouin zone.

    usage: If the Fermi surface data is present as a .bxsf file, which is widely adopted as an output for Fermi
    surface calculations e.g. by Wannier90 or exciting, for building a Fermi surface it is sufficient to just create
    an object of the FermiSurface class and call the build_surface_with_bxsf_files method. Afterwards the visualization
    mehtod can be called

    **Arguments**

    energy_values: list(float)
    List of energies of the electron bands
    In order to visualize Fermi surfaces, the band energy data, the Fermi energy, the reciprocal base vectors,
    as well as the grid size need to be provided (eg. with the `fsvisual.input.read_energy_numbers` function) with creating
    an object of the class. From there the method compute_brillouin_zone must be called to then call the `build_surface()`
    method. Finally, for visualizing the Fermi surface, the visualization method can be called.
    """

    def __init__(self):
        self.energy_values = None
        self.fermi_energy = None
        self.rez_base_vect = None
        self.grid_size = None
        self.brillouin_zone = None
        self.surface = None
        self.fermi_surface_list = None
        self.band_index = None


    @property
    def cartesian_mesh(self):
        return create_cartesian_mesh(self.grid_size)

    def set_energy_values(self, energy_values):
        self.energy_values = energy_values

    def set_fermi_energy(self, fermi_energy):
        self.fermi_energy = fermi_energy

    def set_rez_base_vect(self, rez_base_vect):
        self.rez_base_vect = rez_base_vect

    def set_k_grid_by_size(self, grid_size):
        self.grid_size = grid_size

    def compute_brillouin_zone(self):
        self.brillouin_zone = first_bz(self.rez_base_vect)

    def marching_cubes(self, energyColumn):
        grid_size = self.grid_size
        new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])

        # creates an array with energies taken by the corresponding indices of new_cart_mesh_helper -> created array is
        # as big as the indexing array
        new_cart_mesh_helper = self.energy_values[energyColumn][self.cartesian_mesh.astype(int)]
        new_cart_mesh_helper = np.array(new_cart_mesh_helper).reshape(
            (new_basevect_grid_size[0], new_basevect_grid_size[1],
             new_basevect_grid_size[2]))

        # Apply the Marching Cubes algorithm
        vertices, faces, normals, values = measure.marching_cubes(new_cart_mesh_helper, level=self.fermi_energy)

        # coordinate transformation
        new_basevect_mesh = np.dot(vertices, np.array(self.rez_base_vect))
        ms = pymeshlab.MeshSet()
        ms.add_mesh(pymeshlab.Mesh(new_basevect_mesh, faces))
        new_mesh = ms.current_mesh()

        self.surface = trimesh.Trimesh(vertices=np.asarray(new_mesh.vertex_matrix()),
                                       faces=np.asarray(new_mesh.face_matrix()), process=False)

        return self

    def scale_surface(self, scale_factor):
        if self.surface is None:
            raise ValueError("surface is not yet defined")
        self.surface = scale(scale_factor, self.surface)
        return self

    def center_surface(self):
        if self.surface is None:
            raise ValueError("surface is not yet defined")
        self.surface = centering(self.surface)
        return self

    def slice_surface(self):
        """
        Slices parts of the surface that extend beyond the brillouin zone
        Note: Fermi surface needs to be centered and scaled according to the brillouin zone
        :return: Sliced Fermi surface
        """
        if self.brillouin_zone is None:
            raise ValueError("Brillouin Zone is not yet defined")
        if self.surface is None:
            raise ValueError("surface is not yet defined")

        facet_centers = face_center_BZ(self.brillouin_zone[1])

        # cutting off the surface area outside the 1. BZ
        for i in range(len(self.brillouin_zone[1])):
            facets_normal = np.array(facet_centers[i]) + 1 / 2 * np.array(facet_centers[i])

            self.surface = self.surface.slice_plane(plane_origin=self.brillouin_zone[1][i][0],
                                                    plane_normal=facets_normal * (-1))
        return self

    def subdivide_surface(self, iterations):
        vertices = self.surface.vertices
        faces = self.surface.faces
        self.surface = subdivision_surface(vertices, faces, iterations)
        return self

    def downsample_surface(self, facepercentage):
        vertices = self.surface.vertices
        faces = self.surface.faces
        self.surface = downsample_mesh(vertices, faces, facepercentage)
        return self

    def build_surface_with_bxsf_files(self, filepath, subdivide_iterations=0, down_sampling_percentage=100):

        data = read_energy_numbers(filepath)
        self.set_energy_values(data[0])
        self.set_fermi_energy(data[1])
        self.set_rez_base_vect(data[2])
        self.set_k_grid_by_size(data[3])

        self.compute_brillouin_zone()

        grid_size = self.grid_size
        new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])

        self.band_index = []
        self.fermi_surface_list = []
        for index, columnName in enumerate(self.energy_values.columns):

            # Apply the Marching Cubes algorithm
            try:
                self.marching_cubes(columnName)
            except ValueError:
                continue


            self.subdivide_surface(subdivide_iterations)
            self.downsample_surface(facepercentage=down_sampling_percentage)

            # translation and shrinkage
            self.scale_surface(2 / new_basevect_grid_size)

            # translation
            self.center_surface()

            self.slice_surface()

            self.fermi_surface_list.append(self.surface)
            self.band_index.append(index + 1)  # for the plot
        return self

    def visualization(self, filepath, save_fermisurf_path, svg):
        figure = build_plotly_figure(self.fermi_surface_list, self.brillouin_zone, self.band_index)
        write_figure_to_file(figure, filepath, save_fermisurf_path, create_SVG=svg)
