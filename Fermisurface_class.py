from brilouin_zone import first_bz
from mesh_algorythms import create_cartesian_mesh, face_center_BZ


class FermiSurface:

    def __init__(self, energy_values, fermi_energy, rez_base_vect, grid_size):
        self.energy_values = energy_values
        self.fermi_energy = fermi_energy
        self.rez_base_vect = rez_base_vect
        self.grid_size = grid_size

    def brillouin_zone(self):
        return first_bz(self.rez_base_vect)

    def cartesian_mesh(self):
        return create_cartesian_mesh(self.grid_size)
