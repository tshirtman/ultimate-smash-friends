#!/usr/bin/env bash
rm doc/sphinx/*.rst
for i in $(ls usf/*.py);
do
j=$(echo $i | sed s:.*/::)
echo "
================================================
$j
================================================

.. automodule:: $j
    :members:
    :show-inheritance:


.. toctree::

"|sed s/.py// > doc/sphinx/core.$j.rst
done

for i in $(ls usf/widgets/*.py);
do
j=$(echo $i | sed s:.*/::)
echo "
================================================
$j
================================================

.. automodule:: $j
    :members:
    :show-inheritance:


.. toctree::

"|sed s/.py// > doc/sphinx/widgets.$j.rst
done

for i in $(ls usf/screen/*.py);
do
j=$(echo $i | sed s:.*/::)
echo "
================================================
$j
================================================

.. automodule:: $j
    :members:
    :show-inheritance:


.. toctree::

"|sed s/.py// > doc/sphinx/screen.$j.rst
done

cd doc/sphinx

rm *__init__*

rename s/.py// *.py.rst

echo "
USF modules
===========


.. toctree::
    :maxdepth: 2

" > tmp

for i in $(ls core.*.rst)
do
	echo "    $i" >> tmp
done

mv tmp usf.rst

echo "
widgets
===========


.. toctree::
    :maxdepth: 2

" > tmp

for i in $(ls widgets.*.rst)
do
	echo "    $i" >> tmp
done

mv tmp widgets.rst

echo "
screens
===========


.. toctree::
    :maxdepth: 2

" > tmp

for i in $(ls screen.*.rst)
do
	echo "    $i" >> tmp
done

mv tmp screen.rst

echo "
.. USF documentation master file, created by
   sphinx-quickstart on Mon Feb 21 11:08:19 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root \`toctree\` directive.

Welcome to USF's documentation!
===============================

.. automodule:: usf
    :members:
    :show-inheritance:

Contents:

.. toctree::
   :maxdepth: 2

   usf.rst
   widgets.rst
   screen.rst


Indices and tables
==================

* :ref:\`genindex\`
* :ref:\`modindex\`
* :ref:\`search\`

" > index.rst

