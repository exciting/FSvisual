from brilouin_zone import first_bz
from mesh_algorythms import create_cartesian_mesh, scale, centering,\
                            face_center_BZ, subdivision_surface
from skimage import measure
import numpy as np


class FermiSurface:

    def __init__(self, energy_values, fermi_energy, rez_base_vect, grid_size):
        self.energy_values = energy_values
        self.fermi_energy = fermi_energy
        self.rez_base_vect = rez_base_vect
        self.grid_size = grid_size
        self.brillouin_zone = None  # calculated later on
        self.surface = None  # calculated later on

    def set_surface(self, fermi_surface):
        self.surface = fermi_surface

    def set_brillouin_zone(self):
        self.brillouin_zone = first_bz(self.rez_base_vect)

    def cartesian_mesh(self):
        return create_cartesian_mesh(self.grid_size)

    def marching_cubes(self, mesh):
        return measure.marching_cubes(mesh, level=self.fermi_energy)

    def scale_surface(self, scale_factor):
        if self.surface is None:
            raise ValueError("surface is not yet defined")
        new_surface = scale(scale_factor, self.surface)
        self.surface = new_surface
        return new_surface

    def center_surface(self):
        if self.surface is None:
            raise ValueError("surface is not yet defined")
        new_surface = centering(self.surface)
        self.surface = new_surface
        return new_surface

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

    def subdivide_surface(self, vertices, faces, iterations):
        new_surface = subdivision_surface(self.rez_base_vect, vertices, faces, iterations)
        self.surface = new_surface
        return new_surface
