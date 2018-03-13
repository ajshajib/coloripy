"""
Tests for `coloripy` module.
"""

import numpy as np
from math import isclose
import coloripy as cp


class TestColoripy(object):

    @classmethod
    def setup_class(cls):
        pass

    def test_skew_scale(self):
        modes = ['linear', 'square', 'cubic', 'power', 'sqrt']
        vals = [0., 0.5, 1.]
        for mode, val in zip(modes, vals):
            assert isclose(cp.skew_scale(val, mode=mode), val)

    def test_get_cmap(self):
        standard = np.array([[0.23137255, 0.29803922, 0.75294118],
                         [0.21960784, 0.41568627, 0.87058824],
                         [0.23137255, 0.5372549, 0.97647059],
                         [0.29019608, 0.65490196, 1.0627451 ],
                         [0.39215686, 0.76862745, 1.12941176],
                         [0.52941176, 0.87843137, 1.18039216],
                         [0.67843137, 0.97647059, 1.20784314],
                         [0.84313725, 1.0627451, 1.21568627],
                         [1.00784314, 1.12941176, 1.21176471],
                         [1.17254902, 1.17647059, 1.19607843],
                         [1.32941176, 1.19607843, 1.17647059],
                         [1.2745098 , 1.14901961, 1.03137255],
                         [1.22745098, 1.0745098, 0.87843137],
                         [1.18431373, 0.98431373, 0.7254902 ],
                         [1.14117647, 0.87843137, 0.58431373],
                         [1.09019608, 0.76078431, 0.45490196],
                         [1.03137255, 0.63137255, 0.34901961],
                         [0.96470588, 0.50196078, 0.26666667],
                         [0.88627451, 0.36862745, 0.20784314],
                         [0.8, 0.22745098, 0.17254902],
                         [0.70588235, 0.01568627, 0.14901961]])

        rgb1 = np.array([59, 76, 192])
        rgb2 = np.array([180, 4, 38])
        ref_point = [221., 221., 221.]
        cmap = cp.MshColorMap(rgb1, rgb2, ref_point=ref_point,
                              num_bins=21).get_colormap()

        assert isclose(np.sum(cmap-standard), 0., abs_tol=1e-8)

    @classmethod
    def teardown_class(cls):
        pass
