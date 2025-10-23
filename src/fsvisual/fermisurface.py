from .input import read_energy_numbers
from .brilouin_zone import first_bz
from .visualisation import build_plotly_figure, write_figure_to_file
from .mesh_algorythms import create_cartesian_mesh, face_center_BZ
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
    surface calculations e.g. by Wannier90 or exciting, it is sufficient to just create an object of the FermiSurface
    class and call the build_surface_with_bxsf_files method for building a Fermi surface. Afterwards the visualization
    method can be called to create 3D interactive plots of the Fermi surface.

    For information concerning the .bxsf file format, and also if your fermi surface data is stored in a different format,
    please consult the documentation of FSvisual.
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
        """
        Scales the Fermi surface according to the given `scale_factor`.
        :param scale_factor: factor to scale the Fermi surface by
        :return: self
        """
        if self.surface is None:
            raise ValueError("surface is not yet defined")
        # Create a scaling matrix
        scaling_matrix = np.eye(4)
        scaling_matrix[:3, :3] *= scale_factor

        # Apply the scaling transformation to the mesh
        self.surface.apply_transform(scaling_matrix)
        return self

    def center_surface(self):
        """
        centers the Fermi surface to the origin
        :return: centered Fermi surface as Trimesh object
        """
        if self.surface is None:
            raise ValueError("surface is not yet defined")

        self.surface.apply_translation([-self.surface.centroid[i] for i in range(3)])
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
        """
        divides each triangle of the parsed triangle mesh in to two triangles and therefore
        providing a higher resolution
        :param iterations: how many times this algorithm is applied
        :return: the higher resolution triangle mesh
        """

        vertices = self.surface.vertices
        faces = self.surface.faces

        ms = pymeshlab.MeshSet()

        # Add it to the MeshSet
        ms.add_mesh(pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=faces))
        ms.meshing_surface_subdivision_loop(iterations=iterations, threshold=pymeshlab.PercentageValue(0))

        smoothed_mesh = ms.current_mesh()
        self.surface = trimesh.Trimesh(vertices=np.asarray(smoothed_mesh.vertex_matrix()),
                                        faces=np.asarray(smoothed_mesh.face_matrix()), process=False)

        return self

    def downsample_surface(self, face_percentage, face_numbers):
        """
        lowers the resolution of the Fermi surface mesh (number of faces) to a given percentage
        (from original face count)
        :param face_percentage: targeted face percentage
        :return: self
        """
        if face_percentage == 100 and face_numbers is None:
            return self
        vertices = self.surface.vertices
        faces = self.surface.faces

        ms = pymeshlab.MeshSet()
        # Add it to the MeshSet
        ms.add_mesh(pymeshlab.Mesh(vertex_matrix=vertices, face_matrix=faces))

        if face_numbers is not None and face_percentage != 100:
            raise ValueError("You can only either provide a face_percentage or face_numbers, not both")
        elif face_numbers is not None:
            numFaces = face_numbers
        else:
            facenum = len(faces) * face_percentage / 100
            numFaces = int(facenum)

        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=numFaces)

        smoothed_mesh = ms.current_mesh()
        self.surface = trimesh.Trimesh(vertices=np.asarray(smoothed_mesh.vertex_matrix()),
                                        faces=np.asarray(smoothed_mesh.face_matrix()), process=False)

        return self

    def build_surface_with_bxsf_files(self, filepath, subdivide_iterations=0, down_sampling_percentage=100,
                                      downsampling_surface_face=None):
        """
        whole fermi surface construction process for bxsf files, including reading out the input data, building the
        first brillouin zone and applying the marching cubes' algorithm.
        :param filepath: path to bxsf file.
        :param subdivide_iterations: number of iterations to subdivide the Fermi surface by subdivide_surface
        :param down_sampling_percentage: percentage to which the downsampling_surface method reduces the number of faces
        :param downsampling_surface_face: number of faces to which the downsampling_surface method reduces the mesh
        :return: self
        """

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
            self.downsample_surface(face_percentage=down_sampling_percentage,face_numbers=downsampling_surface_face)

            # translation and shrinkage
            self.scale_surface(2 / new_basevect_grid_size)

            # translation
            self.center_surface()

            self.slice_surface()

            self.fermi_surface_list.append(self.surface)
            self.band_index.append(index + 1)  # for the plot
        return self

    def visualization(self, filepath, save_fermisurf_path, svg=False):
        """
        Visualizes the Fermi surface as a 3D interactive plot saved as an html file. Also allows for creating
        an SVG Image of the Fermi surface along the html file.
        :param filepath: path to bxsf file.
        :param save_fermisurf_path: directory where the created files and imaged will be stored
        :param svg: boolean whether to create the SVG image
        """
        figure = build_plotly_figure(self.fermi_surface_list, self.brillouin_zone, self.band_index)
        write_figure_to_file(figure, filepath, save_fermisurf_path, create_SVG=svg)
