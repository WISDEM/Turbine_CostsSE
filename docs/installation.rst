Installation
------------

.. admonition:: prerequisites
   :class: warning

   NumPy, SciPy, FUSED-Wind, OpenMDAO, CommonSE

Clone the repository at `<https://github.com/WISDEM/Turbine_CostsSE>`_
or download the releases and uncompress/unpack (Turbine_CostsSE.py-|release|.tar.gz or Turbine_CostsSE.py-|release|.zip)

To install Turbine_CostsSE, first activate the OpenMDAO environment and then install with the following command.

.. code-block:: bash

   $ plugin install

To check if installation was successful try to import the module

.. code-block:: bash

    $ python

.. code-block:: python

    > import turbine_costsse.turbine_costsse.turbine_costsse
    > import turbine_costsse.nrel_csm_tcc.nrel_csm_tcc

or run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

.. code-block:: bash

   $ python src/test/test_Turbine_CostsSE.py

An "OK" signifies that all the tests passed.

For software issues please use `<https://github.com/WISDEM/Turbine_CostsSE/issues>`_.  For functionality and theory related questions and comments please use the NWTC forum for `Systems Engineering Software Questions <https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002>`_.

.. only:: latex

    An HTML version of this documentation that contains further details and links to the source code is available at `<http://wisdem.github.io/Turbine_CostsSE>`_

