"""
Make diverging colormaps using the technique presented in "Diverging
Color Maps for Scientific Visualization (Expanded)" by Kenneth Moreland
(http://www.kennethmoreland.com/color-maps/ColorMapsExpanded.pdf).

This library is inspired by and adopted from colorMapCreator.py by Carlo
Bath.
"""

import numpy as np
from matplotlib.colors import LinearSegmentedColormap


class MshColorMap(object):
    """
    Class MshColorMap:
    Create diverging colormaps from RGB1 to RGB2 using the method of Moreland
    or a simple CIELAB-interpolation. num_colors controls the number of color
    values to output (odd number) and divide gives the possibility to output
    RGB-values from 0.0-1.0 instead of 0-255. If a filename different than
    "" is given, the colormap will be saved to this file, otherwise a simple
    output using print will be given.
    """

    def __init__(self, rgb1, rgb2, num_bins=33, divide=255.,
                 method='moreland', ref_point=None):
        """
        :param rgb1:
        :param rgb2:
        :param num_bins: number of bins to make the colormap
        :param divide:
        :param method:
        :param ref_point: mid point of the color map
        """
        self.num_colors = int(num_bins)

        # Transfer-matrix for the conversion of RGB to XYZ color space
        self._transfer_matrix = np.array([[0.4124564, 0.2126729, 0.0193339],
                                         [0.3575761, 0.7151522, 0.1191920],
                                         [0.1804375, 0.0721750, 0.9503041]])
        if ref_point is None:
            self.xn, self.yn, self.zn = 95.047, 100.0, 108.883
        else:
            self.xn, self.yn, self.zn = ref_point

        assert np.mod(self.num_colors, 2) == 1, \
            'For diverging colormaps odd numbers of colors are desireable!'

        known_methods = ['moreland', 'lab']
        assert method in known_methods, 'Unknown method was specified!'

        if method == known_methods[0]:
            self.color_map = self.generate_colormap(rgb1, rgb2, divide)
        elif method == known_methods[1]:
            self.color_map = self.generate_colormap_lab(rgb1, rgb2, divide)

    def get_colormap(self):
        """
        Returns the colormap
        :return:
        """
        return self.color_map

    @staticmethod
    def linearize_rgb(rgb):
        """
        Conversion from the sRGB components to RGB components with physically
        linear properties.
        """

        rgb_linear = np.zeros((3,))

        for i, value in enumerate(rgb):
            value = float(value) / 255.
            if value > 0.04045:
                value = ((value + 0.055) / 1.055) ** 2.4
            else:
                value = value / 12.92
            rgb_linear[i] = value * 100.
        return rgb_linear

    @staticmethod
    def get_srgb(rgb_linear):
        """
        Back conversion from linear RGB to sRGB.
        """

        srgb = np.zeros((3,))

        for i, value in enumerate(rgb_linear):
            value = float(value) / 100.

            if value > 0.00313080495356037152:
                value = (1.055 * np.power(value, 1. / 2.4)) - 0.055
            else:
                value = value * 12.92

            srgb[i] = round(value * 255.)

        return srgb

    def convert_rgb2xyz(self, rgb):
        """
        Conversion of RGB to XYZ using the transfer-matrix
        """
        return np.dot(self.linearize_rgb(rgb), self._transfer_matrix)

    def convert_xyz2rgb(self, xyz):
        """
        Conversion of RGB to XYZ using the transfer-matrix
        :param self:
        :param xyz:
        :return:
        """
        # return np.round(np.dot(xyz,
        #                   np.array(np.matrix(self._transfer_matrix).I)))
        return self.get_srgb(np.dot(xyz,
                            np.array(np.matrix(self._transfer_matrix).I)))

    def convert_rgb2lab(self, rgb):
        """
        Conversion of RGB to CIELAB
        """

        x, y, z = (self.convert_rgb2xyz(rgb)).tolist()

        def helper_func(a):
            limit = 0.008856
            if a > limit:
                return np.power(a, 1./3.)
            else:
                return 7.787*a + 16./116.

        l = 116. * (helper_func(y/self.yn) - (16./116.))
        a = 500. * (helper_func(x/self.xn) - helper_func(y/self.yn))
        b = 200. * (helper_func(y/self.yn) - helper_func(z/self.zn))

        return np.array([l, a, b])

    def convert_lab2rgb(self, lab):
        """
        Conversion of CIELAB to RGB
        """

        l, a, b = lab.tolist()

        def finverse(x):
            x_lim = 0.008856
            a = 7.787
            b = 16. / 116.
            y_lim = a * x_lim + b
            if x > y_lim:
                return np.power(x, 3)
            else:
                return (x - b) / a

        x = self.xn * finverse((a/500.) + (l+16.)/116.)
        y = self.yn * finverse((l+16.)/116.)
        z = self.zn * finverse((l+16.)/116. - (b/200.))

        return self.convert_xyz2rgb(np.array([x, y, z]))

    @staticmethod
    def convert_lab2msh(lab):
        """
        Conversion of CIELAB to Msh
        """

        l, a, b = lab.tolist()

        m = np.sqrt(np.sum(np.power(lab, 2)))
        s = np.arccos(l / m)
        h = np.arctan2(b, a)
        return np.array([m, s, h])

    @staticmethod
    def convert_msh2lab(msh):
        """
        Conversion of Msh to CIELAB
        """

        m, s, h = msh.tolist()

        # calculation of L, a and b
        l = m * np.cos(s)
        a = m * np.sin(s) * np.cos(h)
        b = m * np.sin(s) * np.sin(h)
        return np.array([l, a, b])

    def convert_rgb2msh(self, rgb):
        """ Direct conversion of RGB to Msh. """
        return self.convert_lab2msh(self.convert_rgb2lab(rgb))

    def convert_msh2rgb(self, msh):
        """ Direct conversion of Msh to RGB. """
        return self.convert_lab2rgb(self.convert_msh2lab(msh))

    @staticmethod
    def adjust_hue(msh_saturated, m_unstaturated):
        """
        Function to provide an adjusted hue when interpolating to an
        unsaturated color in Msh space.
        """

        m_saturated, s_saturated, h_saturated = msh_saturated.tolist()

        if m_saturated >= m_unstaturated:
            return h_saturated
        else:
            h_spin = s_saturated * np.sqrt(m_unstaturated**2 - m_saturated**2) / \
                    (m_saturated * np.sin(s_saturated))
            if h_saturated > -np.pi / 3:
                return h_saturated + h_spin
            else:
                return h_saturated - h_spin

    def interpolate_color(self, rgb1, rgb2, interp):
        """
        Interpolation algorithm to automatically create continuous diverging
        color maps.
        """

        msh1 = self.convert_rgb2msh(rgb1)
        m1, s1, h1 = msh1.tolist()
        msh2 = self.convert_rgb2msh(rgb2)
        m2, s2, h2 = msh2.tolist()

        # If points saturated and distinct, place white in middle
        if (s1 > 0.05) and (s2 > 0.05) and (np.abs(h1 - h2) > np.pi / 3.):
            Mmid = max([m1, m2, 88.])
            if interp < 0.5:
                m2 = Mmid
                s2 = 0.
                h2 = 0.
                interp = 2 * interp
            else:
                m1 = Mmid
                s1 = 0.
                h1 = 0.
                interp = 2 * interp - 1.

        # Adjust hue of unsaturated colors
        if (s1 < 0.05) and (s2 > 0.05):
            h1 = self.adjust_hue(np.array([m2, s2, h2]), m1)
        elif (s2 < 0.05) and (s1 > 0.05):
            h2 = self.adjust_hue(np.array([m1, s1, h1]), m2)

        # Linear interpolation on adjusted control points
        msh_mid = (1 - interp) * np.array([m1, s1, h1]) + \
                 interp * np.array([m2, s2, h2])

        return self.convert_msh2rgb(msh_mid)

    def generate_colormap(self, rgb1, rgb2, divide):
        """
        Generate the complete diverging color map using the Moreland-technique
        from RGB1 to RGB2, placing "white" in the middle. The number of points
        given by "numPoints" controls the resolution of the colormap. The
        optional parameter "divide" gives the possibility to scale the whole
        colormap, for example to have float values from 0 to 1.
        """

        # calculate
        scalars = np.linspace(0., 1., self.num_colors)
        RGBs = np.zeros((self.num_colors, 3))
        for i, s in enumerate(scalars):
            RGBs[i, :] = self.interpolate_color(rgb1, rgb2, s)
        return RGBs / divide

    def generate_colormap_lab(self, rgb1, rgb2, divide):
        """
        Generate the complete diverging color map using a transition from
        Lab1 to Lab2, transitioning true RGB-white. The number of points
        given by "numPoints" controls the resolution of the colormap. The
        optional parameter "divide" gives the possibility to scale the whole
        colormap, for example to have float values from 0 to 1.
        """

        lab1 = self.convert_rgb2lab(rgb1)
        lab2 = self.convert_rgb2lab(rgb2)
        lab_white = np.array([100., 0., 0.])

        lab = np.zeros((int(self.num_colors), 3))
        rgbs = np.zeros((int(self.num_colors), 3))
        n2 = np.floor(self.num_colors / 2.)

        for i in range(3):
            lab[0:n2+1, i] = np.linspace(lab1[i], lab_white[i], n2 + 1)
            lab[n2:, i] = np.linspace(lab_white[i], lab2[i], n2 + 1)
        for i, l in enumerate(lab):
            rgbs[i, :] = self.convert_lab2rgb(l)

        return rgbs / divide


def skew_scale(fraction, mode='linear', power=1.):
    """
    Rescale the color distribution to change emphasis.
    :param fraction:
    :param mode:
    :param power:
    :return:
    """
    assert mode in ['linear', 'square', 'cubic', 'power', 'sqrt'], \
        'Rescaling mode not supported!'

    if fraction >= 0.5:
        sign = 1.
    else:
        sign = -1.

    if mode == 'linear':
        return fraction
    elif mode == 'square':
        return (np.abs(fraction - 0.5) / 0.5)**2 * sign*0.5 + 0.5
    elif mode == 'cubic':
        return ((fraction - 0.5) / 0.5)**3 *0.5 + 0.5
    elif mode  == 'power':
        return (np.abs(fraction - 0.5) / 0.5)**power * sign * 0.5 + 0.5
    elif mode == 'sqrt':
        return np.sqrt(np.abs(fraction - 0.5) / 0.5) * sign * 0.5 + 0.5


def get_msh_cmap(rgb1, rgb2, ref=None, num_bins=33, rescale='linear',
                 method='moreland'):
    """
    Returns diverging color map created in Msh space and rescaled.
    Wrapper function to directly utilize the MshColorMap class.
    :param rgb1:
    :param rgb2:
    :param ref:
    :param num_points:
    :param rescale:
    :return:
    """
    colormap = MshColorMap(rgb1, rgb2, num_bins=num_bins,
                           method=method).get_colormap()

    color_dict = {'red': [], 'green': [], 'blue': []}

    n_bins = len(colormap)

    for i, rgb in enumerate(colormap):
        red, green, blue = rgb
        fraction = float(i) / (n_bins - 1)
        color_dict['red'].append((skew_scale(fraction, mode=rescale),
                                  red, red))
        color_dict['green'].append((skew_scale(fraction, mode=rescale),
                                    green, green))
        color_dict['blue'].append((skew_scale(fraction, mode=rescale),
                                   blue, blue))

    msh_cmap = LinearSegmentedColormap('msh', color_dict)

    return msh_cmap
