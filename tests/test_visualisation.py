from fsvisual.visualisation import build_plotly_figure, write_figure_to_file
from fsvisual.brillouin_zone import first_bz
import trimesh
import json
import plotly.io as io
import os


surface_list = trimesh.load("tests/data/visualisation/mesh.ply")    # mesh from bxsf/Ag_fcc_5x5x5.bxsf
rez_lattice = [[0.8152569492, 0.8152569492, -0.8152569492], [0.8152569492, -0.8152569492, 0.8152569492],
               [-0.8152569492, 0.8152569492 , 0.8152569492]]
brillouin_zone_obj = first_bz(rez_lattice)

calculated_figure = build_plotly_figure([surface_list], brillouin_zone_obj, band_index=[4])
with open("tests/data/visualisation/figure.json", "r") as f:
    expected_fig_json = json.load(f)
expected_fig = io.from_json(expected_fig_json)


def compare_dicts(dict1, dict2):

    if dict1.keys() != dict2.keys():    # needs to be refined
        return False
    else:
        return True


def test_build_plotly_figure():
    assert compare_dicts(calculated_figure.to_dict(), expected_fig.to_dict())


def test_write_figure_to_file():
    bool_file_exists = False
    filename = "Ag_fcc_5x5x5"
    write_figure_to_file(expected_fig,f"tests/data/bxsf/{filename}.bxsf", "tests/data" )
    if os.path.exists(f"tests/data/{filename}.html") and os.path.exists(f"tests/data/{filename}.svg"):
        bool_file_exists = True
        os.remove(f"tests/data/{filename}.html")
        os.remove(f"tests/data/{filename}.svg")
    assert bool_file_exists == True



