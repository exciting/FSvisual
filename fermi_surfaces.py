import math

import numpy as np
import trimesh
from skimage import measure
from pymatgen.core import Lattice


def fraction(rez_lattice_vect, s_grid_size):
    """
    used in iterative process of generating the grid for create_mesh()
    :param rez_lattice_vect: second or third rez. lattice vector
    :param s_grid_size: number of datapoints the grid should have along the corresponding lattice vector
    :return: list of s_grid_size points starting at 0 and adds rez_lattice_vect/s_grid_size for each entry plus the
             entry before that
    """
    # fractions to go one grid-Point further each iteration (loop)
    fraction_list = (np.ones((s_grid_size, 3)) * rez_lattice_vect / s_grid_size).tolist()
    fraction_list[0] = [0, 0, 0]

    helper_var = []
    for entry in fraction_list:
        if fraction_list.index(entry) == 0:
            helper_var.append(entry)
        else:
            # adds the last value to the current value in the loop to increase the fraction by each iteration
            helper_var.append((np.array(entry) + np.array(helper_var[-1])).tolist())
    fraction_list = helper_var
    return fraction_list


def xc_malloc_tensor3f(x, y, z):
    return np.zeros((x, y, z), dtype=float)


def create_mesh(rez_lattice, grid_size, brillouin_zone):
    """
    creates a mesh within the reciprocal unit cell for any reciprocal lattice
    creates second mesh (mol) where energy placeholders are stored to be replaced by real energy values
    later on -> very important for fermi_surface shape

    :param brillouin_zone: facets and vertices of the first BZ are needed
    :param direct_lattice: koordinates for the reciprocal lattice vectors (list of three 3 Dimensional koordinates)
    :param grid_size: number of datapoints the grid should have (list of 3 number for each lattice vector)
    :return: standard mesh and mol mesh
    """

    reciprocal_lattice = Lattice([rez_lattice[0], rez_lattice[1], rez_lattice[2]])

    # Umwandlung in das direkte Gitter
    direct_lattice = reciprocal_lattice.reciprocal_lattice.matrix

    grid_size = [int(grid_size_n) for grid_size_n in grid_size]
    mesh = []

    fraction1 = fraction(rez_lattice[1], grid_size[1])  # for generating basic mesh
    fraction2 = fraction(rez_lattice[2], grid_size[2])

    frmin = [1.0, 1.0, 1.0]  # placeholder for min and max vector of the fermi_surface
    frmax = [-1.0, -1.0, -1.0]
    Imin = [0] * 3
    Imax = [0] * 3
    frImin = [0.0] * 3
    frImax = [0.0] * 3
    band_grid = xc_malloc_tensor3f(grid_size[0], grid_size[1], grid_size[2])

    # loop that creates the mesh
    p = 0
    for i in range(0, grid_size[0]):
        for j in range(0, grid_size[1]):
            for k in range(0, grid_size[2]):
                v = np.array(rez_lattice[0]) / grid_size[0] * i + fraction1[j] + fraction2[k]
                mesh.append(v)
                band_grid[i, j, k] = p  # placeholder to create mol grid
                p += 1

    grid_size_minus_one = [grid - 1 for grid in grid_size]

    for i in range(len(brillouin_zone[1])):  # facet
        for j in range(len(brillouin_zone[1][i])):  # vertex
            for k in range(3):  # finding real min and max vector of fermi_surface
                a = (brillouin_zone[1][i][j][0] * direct_lattice[k][0]
                     + brillouin_zone[1][i][j][1] * direct_lattice[k][1]
                     + brillouin_zone[1][i][j][2] * direct_lattice[k][2])
                if a < frmin[k]:
                    frmin[k] = a
                if a > frmax[k]:
                    frmax[k] = a
    for k in range(3):
        Imin[k] = -grid_size_minus_one[k]
        Imax[k] = grid_size_minus_one[k]

        frImin[k] = float(Imin[k]) / grid_size_minus_one[k]
        frImax[k] = float(Imax[k]) / grid_size_minus_one[k]

    # creating the mols dictionary
    mols = {'i': Imax[0] - Imin[0] + 1, 'j': Imax[1] - Imin[1] + 1, 'k': Imax[2] - Imin[2] + 1, 'lowcoor': [0, 0, 0],
            "molgrid": xc_malloc_tensor3f(grid_size[0], grid_size[1], grid_size[2])}
    mols["molgrid"] = xc_malloc_tensor3f(mols["i"], mols["j"], mols["k"])
    for k in range(3):
        mols['lowcoor'][k] = (frImin[0] * direct_lattice[k][0] +
                              frImin[1] * direct_lattice[k][1] +
                              frImin[2] * direct_lattice[k][2])
        # for j in range(3):
        #    mols['vec'][k][j] = (frImax[k] - frImin[k]) * rez_lattice[k][j]
        #    mols['isoexpand']['rep_vec'][k][j] = rez_lattice[k][

    for i1, i in enumerate(range(int(Imin[0]), int(Imax[0]) + 1)):
        ii = i if i >= 0 else grid_size_minus_one[0] + i
        for j1, j in enumerate(range(int(Imin[1]), int(Imax[1]) + 1)):
            jj = j if j >= 0 else grid_size_minus_one[1] + j
            for k1, k in enumerate(range(int(Imin[2]), int(Imax[2]) + 1)):
                kk = k if k >= 0 else grid_size_minus_one[2] + k
                mols['molgrid'][i1][j1][k1] = band_grid[ii, jj, kk]
    return mesh, mols


def crop_BZ(fermisurf, Brillouin_Zone):
    # marching cubes:
    triangulized = measure.marching_cubes(fermisurf, 0)

    for triangle in triangulized:
        for i in range(3):
            index = triangle


# def energy_selection(band_energies):


def triangulate_faces(facets):
    """
    splits every facet of the 1. BZ into triangles for Trimesh to read -> function is used by brillouin_intersect_mesh()
    :param facets: list of all facets with vertices counted from 0 to last vertex
    :return:
    """
    triangles = []
    for facet in facets:
        if len(facet) == 3:
            triangles.append(facet)
        elif len(facet) == 4:
            triangles.append([facet[0], facet[1], facet[2]])
            triangles.append([facet[0], facet[2], facet[3]])
        else:
            # For facets with more than 4 vertices, use a fan triangulation
            for i in range(1, len(facet) - 1):
                triangles.append([facet[0], facet[i], facet[i + 1]])
    return triangles


def brillouin_intersect_mesh(brillouin_zone):
    """
    modulates a 3D mesh in shape of the 1. BZ to tell whether a point lies within the 1. BZ or not

    :param brillouin_zone: list of all facets of the 1. BZ, within the facets shall be all vertices of the facet
    :return: modulated 1. BZ as a Trimesh object
    """
    # creates a list with information on how the lines are connected
    facet_order_list = []
    helper_brillouin_zone = []

    number_val_BZ = sum(len(facet) for facet in brillouin_zone)

    j = 0
    for facet in brillouin_zone:
        facet_order = [i for i in range(j, j + len(facet)) if i < number_val_BZ + 1]
        j += len(facet_order)
        if len(facet_order) != 0:
            facet_order_list.append(facet_order)
        helper_brillouin_zone.extend(facet)
    brillouin_zone = helper_brillouin_zone

    # Triangulate the faces
    triangulated_faces = triangulate_faces(facet_order_list)

    brillouin_zone_object = trimesh.Trimesh(vertices=brillouin_zone, faces=triangulated_faces)

    return brillouin_zone_object


def fold_to_first_bz(mesh_point, brillouin_zone, bz_model):
    # attempt for folding algorithm
    # create plane:
    for facet in brillouin_zone:
        plane_vect1 = np.array(facet[0])
        plane_vect2 = np.array(facet[1])
        plane_vect3 = np.array(facet[2])

        n = np.cross(plane_vect2, plane_vect3)

        # plane in coordinate_form
        # d = n1*v1 + n2*v2 + n3*v3
        d = n[0] * plane_vect1[0] + n[1] * plane_vect1[1] + n[2] * plane_vect1[2]

        # create line
        # (mesh_point + x*n) in plane equation
        a = np.dot(n, n)
        b = d - np.dot(n, mesh_point)

        # a*x = b

        x = b / a

        intersection_point = mesh_point + x * n

        length = np.sqrt(np.dot(mesh_point - intersection_point, mesh_point - intersection_point))

        # normalize n:
        n_norm_const = np.sqrt(1 / np.dot(n, n))
        n_norm = n * n_norm_const

        # calculate mirrored point
        p_mirror = mesh_point + 2 * length * n_norm

        if bz_model.contains([p_mirror])[0]:
            return p_mirror
    return [0, 0, 0]


def check_fermi_surface(energies, fermi_energy):
    """
    checks whether the energy in a band is equal to the fermi_energy (within uncertainties)
    :param fermi_energy: energy value that FERMISURF.bxsf defines as fermiy_energy
    :param energies: all energy values of one band
    :return: list of indices for k-points to choose from the grid
    """

    index_for_k_position = []
    i = 0
    for energy in energies:
        if fermi_energy - 0.01 <= energy <= fermi_energy + 0.01:
            index_for_k_position.append(i)
        i += 1
    return index_for_k_position


def marching_cubes_clip(rez_vec, facets, vertices, brillouin_zone_object, grid_size):

    ### not in use, different approach
    vertices = vertices.tolist()
    facets = facets.tolist()
    j = 0
    for i, vertex in enumerate(vertices):  # scale mesh to first BZ
        vertex[0] = vertex[0] / grid_size * np.sqrt(rez_vec[0][0] ** 2 + rez_vec[0][1] ** 2 + rez_vec[0][2] ** 2)
        vertex[1] = vertex[1] / grid_size * np.sqrt(rez_vec[0][0] ** 2 + rez_vec[0][1] ** 2 + rez_vec[0][2] ** 2)
        vertex[2] = vertex[2] / grid_size * np.sqrt(rez_vec[0][0] ** 2 + rez_vec[0][1] ** 2 + rez_vec[0][2] ** 2)
        vertices[i] = vertex
        if brillouin_zone_object.contains([vertex]):
            pass
        else:
            #facets = np.delete(facets, math.ceil(i / 3))  # round up to next integer, so that the right facet is deleted
            #vertices = np.delete(vertices, i)
            for k, facet in enumerate(facets):
                if (facet[0] or facet[1] or facet[2]) == i:
                    del facets[k]
            del facets[math.ceil((i-j) / 3)]
            del vertices[i-j]
    return vertices, facets
