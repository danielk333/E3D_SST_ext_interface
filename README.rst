EISCAT 3D SST External Interface
=====================================


Install
-----------------

Requires python>=3.7

.. code-block:: bash

    #First install sorts
    git clone https://github.com/danielk333/SORTS
    cd sorts
    pip install .
    cd ..

    #Then install the external interface
    git clone https://github.com/danielk333/E3D_SST_ext_interface
    cd E3D_SST_ext_interface
    pip install -r requirements

    #Then test the implementation
    pytest


Running
---------------

To start the SST Services daemon that includes a delivery client

.. code-block:: python

   python server.py start


To stop daemon

.. code-block:: python

   python server.py stop


To restart daemon

.. code-block:: python

   python server.py restart


Or to simply run in the terminal

.. code-block:: python

   python server.py run


