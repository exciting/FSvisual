from pymatgen.core import Lattice


def first_bz(rez_lattice):

    """
    calculates the edge points of a Brillouin zone for any given reciprocal lattice.

    :param rez_lattice: coordinates for the reciprocal lattice vectors (list of three 3 Dimensional coordinates)
    :return: 1. Brillouin zone as a list containing x, y, z coordinates on separate lists for each
    """

    new_lattice = Lattice(rez_lattice)
    brillouin_zone = new_lattice.get_wigner_seitz_cell()

    # Prepare data for Plotly
    x, y, z = [], [], []
    for facet in brillouin_zone:
        # brillouin zone consists of many facets -> facets consists of vertices (edge points -> koordinates)
        # Ensure each facet is closed by adding the first vertex at the end
        facet.append(facet[0])
        for vertex in facet:
            x.append(vertex[0])
            y.append(vertex[1])
            z.append(vertex[2])
        # Add None to create a break in the plot lines between facets
        x.append(None)
        y.append(None)
        z.append(None)
    brillouin_zone_xyz = [x, y, z]
    return brillouin_zone_xyz, brillouin_zone




