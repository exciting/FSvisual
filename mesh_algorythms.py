import numpy as np
import trimesh
import pymeshlab


def create_cartesian_mesh(grid_size):
    """
    creates a mesh within the reciprocal unit cell for any reciprocal lattice
    :param grid_size: number of datapoints the grid should have (list of 3 number for each lattice vector)
    :return: standard mesh
    """

    grid_size = [int(grid_size_n) for grid_size_n in grid_size]
    Imin = [0] * 3
    Imax = [0] * 3

    # loop that creates the mesh

    band_grid = np.arange((grid_size[0]) * (grid_size[1]) * (grid_size[2]))
    band_grid = band_grid.reshape((grid_size[0], grid_size[1], grid_size[2]))

    grid_size_minus_one = [grid - 1 for grid in grid_size]

    for k in range(3):
        Imin[k] = -int(grid_size_minus_one[k])
        Imax[k] = int(grid_size_minus_one[k])

    # creating the mols
    mesh_axis_one = np.arange(Imin[0], Imax[0] + 1)
    mesh_axis_two = np.arange(Imin[1], Imax[1] + 1)
    mesh_axis_three = np.arange(Imin[2], Imax[2] + 1)

    mesh_axis_one = np.where(mesh_axis_one >= 0, mesh_axis_one, mesh_axis_one + grid_size_minus_one[0])
    mesh_axis_two = np.where(mesh_axis_two >= 0, mesh_axis_two, mesh_axis_two + grid_size_minus_one[1])
    mesh_axis_three = np.where(mesh_axis_three >= 0, mesh_axis_three, mesh_axis_three + grid_size_minus_one[2])

    index_mesh = np.ix_(mesh_axis_one, mesh_axis_two, mesh_axis_three)

    cartesian_mesh = band_grid[index_mesh].flatten()

    return cartesian_mesh


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


def abs_vect(vector):
    """
    :param vector: takes 3D vector as a list or array
    :return: absolute value of that vector
    """
    return np.sqrt(vector[0] ** 2 + vector[1] ** 2 + vector[2] ** 2)


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

    area = 1 / 2 * np.sqrt(abs_vect(P2 - P1) ** 2 * abs_vect(P3 - P1) ** 2 - np.dot((P2 - P1), (P3 - P1)) ** 2)
    return area


def triangle_center(triangle):
    """
    calculates the center of every triangle
    :param triangle: list of 3 vertices
    :return: center point of a triangle
    """

    xS = 1 / 3 * (triangle[0][0] + triangle[1][0] + triangle[2][0])
    yS = 1 / 3 * (triangle[0][1] + triangle[1][1] + triangle[2][1])
    zS = 1 / 3 * (triangle[0][2] + triangle[1][2] + triangle[2][2])

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
        for triangle in triangle_list[j:j + len(facet) - 2]:  # goes through every triangle of each facet
            # triangle area:
            if triangle_area(triangle) != 0:
                triangle_areas.append(triangle_area(triangle))  # triangle area
                triangle_centers.append(triangle_center(triangle))  # triangle center
        j += len(facet) - 2

        x_coord = np.array([point[0] for point in triangle_centers])
        y_coord = np.array([point[1] for point in triangle_centers])
        z_coord = np.array([point[2] for point in triangle_centers])

        # calculation of the facet center (geometrischer Schwerpunkt)
        xS = np.sum(x_coord * np.array(triangle_areas)) / np.sum(triangle_areas)
        yS = np.sum(y_coord * np.array(triangle_areas)) / np.sum(triangle_areas)
        zS = np.sum(z_coord * np.array(triangle_areas)) / np.sum(triangle_areas)

        face_centers.append([xS, yS, zS])

    return face_centers


def scale(scale_factor, fermi_surface):
    """
    Scales the Fermi surface in size
    :param scale_factor: factor by which the surface scales
    :param fermi_surface: Fermi surface as a Trimesh object
    :return: Fermi surface as Trimes object
    """
    # scale_factors = 2 / new_basevect_grid_size  # 2 wegen Durchmesser 1. BZ  # nochmal gucken.

    # Create a scaling matrix
    scaling_matrix = np.eye(4)
    scaling_matrix[:3, :3] *= scale_factor

    # Apply the scaling transformation to the mesh
    fermi_surface.apply_transform(scaling_matrix)

    return fermi_surface


def centering(fermi_surface):
    """
    centers the Fermi surface to the origin
    :param fermi_surface: Fermi surface as Trimesh object
    :return: centered Fermi surface as Trimesh object
    """

    fermi_surface.apply_translation(
        [-fermi_surface.centroid[0], -fermi_surface.centroid[1], -fermi_surface.centroid[2]])

    return fermi_surface


def subdivision_surface(rez_base_vect, vertices, faces, iterations):
    new_basevect_mesh = np.dot(vertices, np.array(rez_base_vect))

    ms = pymeshlab.MeshSet()
    ms.add_mesh(pymeshlab.Mesh(new_basevect_mesh, faces))

    # strength of smoothing should adapt with input mesh size
    ms.meshing_surface_subdivision_loop(iterations=iterations)

    smoothed_mesh = ms.current_mesh()
    fermi_surface = trimesh.Trimesh(vertices=np.asarray(smoothed_mesh.vertex_matrix()),
                                    faces=np.asarray(smoothed_mesh.face_matrix()), process=False)

    return fermi_surface
