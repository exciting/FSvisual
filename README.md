# FSvisual
FSvisual is a software tool to visualize **Fermi surfaces**—the boundaries 
between occupied and unoccupied electronic states in metals.

It is capable of creating interactive 3D Fermi surface 
visualizations on a 2D screen as an <span style="font-family: monospace; font-weight: bold;">html</span> 
file format. Those visualizations can be accessed via any web browser,
as shown in the image below with the Fermi surface of Be as an example.

![Fermi surface visualization of Be by FSvisual](images/Be_fermi_surface.png)
<div style="width: 100%; max-width: 1000px; margin: 0 auto;">
  <img
    src="images/Be_fermi_surface.png"
    alt="Fermi surface visualization of Be by FSvisual"
    style="width: 100%; height: auto; display: block;"
  >
</div>


The significance of Fermi surfaces arises from a fundamental physical principle:
Only energy states in close proximity to the Fermi surface can actively participate
in a material’s response to external stimuli at temperatures around and below room
temperature. Consequently, the topology and characteristics of Fermi surfaces
strongly determine many material properties, including electronic, optical, thermal,
and magnetic properties.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#Dependencies)
- [License](#license)

## Installation
## Usage
After the installation, **FSvisual** can be launched via a command line
interface (CLI) by typing the command `fsvisual` into your console. 
**FSvisual** requires you to provide a directory or file path to your
Fermi surface file/files. Currently, **FSvisual** only supports Fermi surface
data in the **.bxsf** file format, which was established by visualization
software XCrySDen and is now widely adopted by software supporting 
Fermi surface calculation, including <span style="font-family: monospace; font-weight: bold;">exciting</span>.
In the following you can find an example on how to correctly call FSvisual 
together with one of its optional arguments.

```bash
fsvisual "bxsf_file_or_directory_path" -sf "save_path"
```
This command starts the visualization of the Fermi surface calculations
stored in the specified directory, and saves them to the specified *save_path*.
By typing `fsvisual -h` you get a list of all available arguments 
along with an explanation on how to use them:


```
usage: fsvisual [-h] [-sf SAVE_FERMISURFACES] [-s SUBDIVISION_SURFACE] [-dp DOWNSAMPLING_SURFACE_PERCENTAGE]
                [-df DOWNSAMPLING_SURFACE_FACE] [-c]
                bxsf_files_directory

positional arguments:
  bxsf_files_directory  directory (folder) where the .bxsf files (Fermisurface files) are stored

options:
  -h, --help            show this help message and exit
  -sf SAVE_FERMISURFACES, --save_fermisurfaces SAVE_FERMISURFACES
                        directory where visualized Fermi surfaces are stored
  -s SUBDIVISION_SURFACE, --subdivision_surface SUBDIVISION_SURFACE
                        divides every triangle of the Fermi surface mesh into two triangles; executes as many times as
                        the input says
  -dp DOWNSAMPLING_SURFACE_PERCENTAGE, --downsampling_surface_percentage DOWNSAMPLING_SURFACE_PERCENTAGE
                        lowers the resolution of the Fermi surface mesh (number of faces) to a given percentage (from
                        original face count)
  -df DOWNSAMPLING_SURFACE_FACE, --downsampling_surface_face DOWNSAMPLING_SURFACE_FACE
                        lowers the resolution of the Fermi surface mesh (number of faces) to a given face number
  -c, --create_SVG      boolean whether to create SVG files 
```
Once the Fermi surfaces of interest are visualized and opened 
in a web browser of choice, the camera view of every surface 
created by FSvisual can be rotated by holding the left 
mouse button and dragging the cursor in the desired 
direction. Holding the right mouse button (or
pressing the control key on the keyboard + left mouse button) locks the vertical
axis of the camera. Subsequent movements will translate the camera along the
horizontal axes. Any alteration of the camera position can be reset by reloading the
page. The user can zoom in and out using the mouse wheel. An interactive legend
is located in the upper-right corner of the screen. By clicking
the entries in the legend, the user can either hide or show
the first Brillouin zone as well as the different surface parts
that are contributions from different energy bands to the Fermi
surface. This functionality is illustrated in the image below.

<div style="width: 100%; max-width: 1000px; margin: 0 auto;">
  <img
    src="images/FSvisual_demo.png"
    alt="Illustrates the functionality to show and hide surface 
parts as well as the first Brillouin zone with the Legend"
    style="width: 100%; height: auto; display: block;"
  >
</div>

## Dependencies

<custom-element data-json="%7B%22type%22%3A%22table-metadata%22%2C%22attributes%22%3A%7B%22title%22%3A%22Dependencies%22%7D%7D" />

| Package   | Version | Link                                                                         |
|-----------|---------|------------------------------------------------------------------------------|
| Python    | ≥ 3.9   | [python.org](https://python.org)                                             |
| `pandas`  | ≥ 2.3.1 | [pandas.pydata.org](https://pandas.pydata.org/)                              |
| `numpy`   | ≥ 2.3.1  | [numpy.org](https://numpy.org)                                               |
| `trimesh` | ≥ 4.7.4   | [trimesh.org](https://trimesh.org/)                                          |
| `pymeshlab`| ≥ 2023.12.post3   | [pymeshlab.readthedocs.io](https://pymeshlab.readthedocs.io/en/latest/)      |
| `scikit-image`  | ≥ 0.25.2   | [scikit-image.org](https://scikit-image.org/)                                |
| `requests` | ≥ 2.32.4   | [python-requests.org](https://docs.python-requests.org/en/latest/index.html) |
| `pymatgen`| ≥ 2025.6.14   | [pymatgen.org](https://pymatgen.org/)                                        |
| `plotly`  | ≥ 6.3.0   | [plotly.com](https://plotly.com/python/)                                     |
| `shapely`| ≥ 2.1.1  | [shapely](https://github.com/shapely/shapely)                                |
| `kaleido`  | ≥ 1.0.0   | [kaleido](https://pypi.org/project/kaleido/)                                        |


## License
This project is licensed under the 
[GNU General Public License](LICENSE).

**References:** 

Stutz, J. (2025). *Visualization of Fermi Surfaces
for Large-Scale Databases* [Bachelor’s thesis, Humboldt Universität zu Berlin].