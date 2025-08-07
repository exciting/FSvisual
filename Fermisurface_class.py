from brilouin_zone import first_bz
from visualisation import build_plotly_figure, write_figure_to_file
from mesh_algorythms import create_cartesian_mesh, scale, centering, \
    face_center_BZ, subdivision_surface
from skimage import measure
import numpy as np
from copy import deepcopy
import trimesh


class FermiSurface:

    def __init__(self, energy_values, fermi_energy, rez_base_vect, grid_size):
        self.energy_values = energy_values
        self.fermi_energy = fermi_energy
        self.rez_base_vect = rez_base_vect
        self.grid_size = grid_size
        self.brillouin_zone = None  # calculated later on
        self.surface = None  # calculated later on
        self.fermi_surface_list = None
        self.band_index = None

    def set_surface(self, fermi_surface):
        self.surface = fermi_surface

    def set_brillouin_zone(self):
        self.brillouin_zone = first_bz(self.rez_base_vect)

    def cartesian_mesh(self):
        return create_cartesian_mesh(self.grid_size)

    def marching_cubes(self, energyColumn):
        grid_size = self.grid_size
        new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])

        new_cart_mesh_helper = deepcopy(self.cartesian_mesh())
        # creates an array with energies taken by the corresponding indices of new_cart_mesh_helper -> created array is
        # as big as the indexing array
        new_cart_mesh_helper = self.energy_values[energyColumn][new_cart_mesh_helper.astype(int)]
        new_cart_mesh_helper = np.array(new_cart_mesh_helper).reshape(
            (new_basevect_grid_size[0], new_basevect_grid_size[1],
             new_basevect_grid_size[2]))
        print("done")

        # Apply the Marching Cubes algorithm
        vertices, faces, normals, values = measure.marching_cubes(new_cart_mesh_helper, level=self.fermi_energy)

        self.surface = trimesh.Trimesh(vertices=np.asarray(vertices),
                                       faces=np.asarray(faces), process=False)

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
        self.surface = subdivision_surface(self.rez_base_vect, vertices, faces, iterations)
        return self

    def build_surface(self):
        grid_size = self.grid_size
        new_basevect_grid_size = np.array([grid_size[0] * 2 - 1, grid_size[1] * 2 - 1, grid_size[2] * 2 - 1])

        self.band_index = []
        self.fermi_surface_list = []
        for index, columnName in enumerate(self.energy_values.columns):

            # Apply the Marching Cubes algorithm
            try:
                self.marching_cubes(columnName)
            except ValueError:
                "nothing here"
                continue

            # transform vertices, so it fits the base_vect_grid
            self.subdivide_surface(2)

            # translation and shrinkage

            # 2 wegen Durchmesser 1. BZ  # nochmal gucken.
            self.scale_surface(2 / new_basevect_grid_size)

            # translation
            self.center_surface()

            self.slice_surface()

            self.fermi_surface_list.append(self.surface)
            self.band_index.append(index + 1)  # for the plot
        return self

    def visualization(self, filepath, save_fermisurf_path):
        figure = build_plotly_figure(self.fermi_surface_list, self.brillouin_zone, self.band_index)
        write_figure_to_file(figure, filepath, save_fermisurf_path)



