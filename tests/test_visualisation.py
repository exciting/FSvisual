from fsvisual.visualisation import build_plotly_figure, write_figure_to_file
from fsvisual.brillouin_zone import first_bz
import trimesh
import json
import plotly.io as io
import numpy as np


surface_list = trimesh.load("tests/data/visualisation/mesh.ply")    # mesh from bxsf/Ag_fcc_5x5x5.bxsf
rez_lattice = [[0.8152569492, 0.8152569492, -0.8152569492], [0.8152569492, -0.8152569492, 0.8152569492],
               [-0.8152569492, 0.8152569492 , 0.8152569492]]
brillouin_zone_obj = first_bz(rez_lattice)

calculated_figure = build_plotly_figure([surface_list], brillouin_zone_obj, band_index=[4])
with open("tests/data/visualisation/figure.json", "r") as f:
    expected_fig_json = json.load(f)
expected_fig = io.from_json(expected_fig_json)


def compare_vertices_dicts(dict1, dict2):

    if dict1.keys() != dict2.keys():    # needs to be refined
        return False
    else:
        # compare vertices of the figure
        dict1_data = [dict1["data"][0]["x"], dict1["data"][0]["y"], dict1["data"][0]["z"]]
        dict2_data = [dict2["data"][0]["x"], dict2["data"][0]["y"], dict2["data"][0]["z"]]
        for j in range(len(dict1_data)):
            for k in range(len(dict1_data[j])):
                if dict1_data[j][k] is None:
                    dict1_data[j][k] = np.nan
                if dict2_data[j][k] is None:
                    dict2_data[j][k] = np.nan

        return np.allclose(dict1_data, dict2_data, equal_nan = True)


def test_build_plotly_figure():
    assert compare_vertices_dicts(calculated_figure.to_dict(), expected_fig.to_dict()), "not all vertices are the same!"


