=============================
Coloripy
=============================

.. image:: https://badge.fury.io/py/coloripy.png
    :target: http://badge.fury.io/py/coloripy

.. image:: https://travis-ci.org/ajshajib/coloripy.png?branch=master
    :target: https://travis-ci.org/ajshajib/coloripy

A package to make beautiful diverging color maps in Msh space. For technical details, see "Diverging Color Maps for Scientific Visualization (Expanded)" by Kenneth Moreland (http://www.kennethmoreland.com/color-maps/ColorMapsExpanded.pdf).



Features
--------

* Make aesthetically pleasing diverging color-maps in the Msh space.

Installation
------------

.. code-block:: bash

    $ git clone https://github.com/ajshajib/coloripy.git
    $ cd coloripy
    $ python setup.py install --user


Usage Example
-------
.. code-block:: python

    import coloripy as cp
    msh_cmap = cp.get_msh_cmap()
