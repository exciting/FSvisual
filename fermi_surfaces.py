import numpy as np
import trimesh
from skimage import measure
from pymatgen.core import Lattice


def xc_malloc_tensor3f(x, y, z):
    return np.zeros((x, y, z), dtype=float)


def create_mol_mesh(grid_size):
    """
    creates a mesh within the reciprocal unit cell for any reciprocal lattice
    creates second mesh (mol) where energy placeholders are stored to be replaced by real energy values
    later on -> very important for fermi_surface shape

    :param grid_size: number of datapoints the grid should have (list of 3 number for each lattice vector)
    :return: standard mesh and mol mesh
    """

    grid_size = [int(grid_size_n) for grid_size_n in grid_size]
    Imin = [0] * 3
    Imax = [0] * 3

    # loop that creates the mesh

    band_grid = np.arange((grid_size[0])*(grid_size[1])*(grid_size[2]))
    band_grid = band_grid.reshape((grid_size[0], grid_size[1], grid_size[2]))

    grid_size_minus_one = [grid - 1 for grid in grid_size]

    for k in range(3):
        Imin[k] = -int(grid_size_minus_one[k])
        Imax[k] = int(grid_size_minus_one[k])

    # creating the mols dictionary
    mols = {'i': Imax[0] - Imin[0] + 1, 'j': Imax[1] - Imin[1] + 1, 'k': Imax[2] - Imin[2] + 1}
    mols["molgrid"] = xc_malloc_tensor3f(mols["i"], mols["j"], mols["k"])
    mols["molgrid"] = np.zeros((grid_size[0]*2-1)*(grid_size[1]*2-1)*(grid_size[2]*2-1))
    p = 0
    for i1, i in enumerate(range(Imin[0], Imax[0] + 1)):
        ii = i if i >= 0 else grid_size_minus_one[0] + i
        for j1, j in enumerate(range(Imin[1], Imax[1] + 1)):
            jj = j if j >= 0 else grid_size_minus_one[1] + j
            for k1, k in enumerate(range(Imin[2], Imax[2] + 1)):
                kk = k if k >= 0 else grid_size_minus_one[2] + k
                #mols['molgrid'][i1][j1][k1] = band_grid[ii, jj, kk]
                mols["molgrid"][p] = band_grid[ii, jj, kk]
                p +=1

    return mols


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


def check_fermi_surface(energies, fermi_energy):
    # outdated
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


def abs_vect(vector):
    """
    :param vector: takes 3D vector as a list or array
    :return: absolute value of that vector
    """
    return np.sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)


def triangle_area(triangle):

    """
    calculates the area of a triangle via vertices
    :param triangle: list of 3 vertices
    :return: area of a triangle in FE
    """

    # nach Koordinaten im Raum

    P1 = np.array(triangle[0])
    P2 = np.array(triangle[1])
    P3 = np.array(triangle[2])

    area = 1/2 * np.sqrt(abs_vect(P2-P1)**2 * abs_vect(P3-P1)**2 - np.dot((P2-P1), (P3-P1))**2)
    return area


def triangle_center(triangle):

    """
    calculates the center of every triangle
    :param triangle: list of 3 vertices
    :return: center point of a triangle
    """

    xS = 1/3 * (triangle[0][0] + triangle[1][0] + triangle[2][0])
    yS = 1/3 * (triangle[0][1] + triangle[1][1] + triangle[2][1])
    zS = 1/3 * (triangle[0][2] + triangle[1][2] + triangle[2][2])

    return [xS, yS, zS]


def face_center_BZ(brillouin_zone_facets):

    """
    function to calculate the center of every facet
    :param brillouin_zone_facets: list with all facets (filled with points, not indices)
    :return: list of 3D center points for every facet
    """

    # triangulate the facets:
    triangle_list = triangulate_faces(brillouin_zone_facets)

    face_centers = []
    j = 0
    for facet in brillouin_zone_facets:  # goes through every facet and calculates the center of it
        triangle_areas = []
        triangle_centers = []
        for triangle in triangle_list[j:j+len(facet)-2]:  # goes through every triangle of each facet
            # triangle area:
            if triangle_area(triangle) != 0:
                triangle_areas.append(triangle_area(triangle))  # triangle area
                triangle_centers.append(triangle_center(triangle))  # triangle center
        j += len(facet)-2

        x_coord = np.array([point[0] for point in triangle_centers])
        y_coord = np.array([point[1] for point in triangle_centers])
        z_coord = np.array([point[2] for point in triangle_centers])

        # calculation of the facet center (geometrischer Schwerpunkt)
        xS = np.sum(x_coord * np.array(triangle_areas)) / np.sum(triangle_areas)
        yS = np.sum(y_coord * np.array(triangle_areas)) / np.sum(triangle_areas)
        zS = np.sum(z_coord * np.array(triangle_areas)) / np.sum(triangle_areas)

        face_centers.append([xS, yS, zS])

    return face_centers
