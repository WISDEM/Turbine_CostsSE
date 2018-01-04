Turbine_CostsSE is a set of models for assessing the costs of a wind turbine.  The first model is based on the NREL Cost and Scaling Model which uses component mass information as well as key turbine parameters such as rotor diameter, rated power and hub height to cost out the whole turbine.  A second model is a new mass-to-cost model which takes the individual component masses as inputs to estimate each component costs with additional cost factors for assembly, overhead, and profits.  A third is a new version of NREL's turbine cost and sizing tool that uses data for component sizes and costs in the year 2015.

Author: [K. Dykes](mailto:nrel.wisdem+turbinecostsse@gmail.com)

## Version

This software is a beta version 0.1.1.

## Detailed Documentation

For detailed documentation see <http://wisdem.github.io/Turbine_CostsSE/>

## Prerequisites

General: NumPy, SciPy, Swig, pyWin32, MatlPlotLib, Lxml, OpenMDAO

## Dependencies:

Wind Plant Framework: [FUSED-Wind](http://fusedwind.org) (Framework for Unified Systems Engineering and Design of Wind Plants)

Sub-Models: CommonSE

Supporting python packages: Pandas, Algopy, Zope.interface, Sphinx, Xlrd, PyOpt, py2exe, Pyzmq, Sphinxcontrib-bibtex, Sphinxcontrib-zopeext, Numpydoc, Ipython

## Installation

First, clone the [repository](https://github.com/WISDEM/Turbine_CostsSE)
or download the releases and uncompress/unpack (Turbine_CostsSE.py-|release|.tar.gz or Turbine_CostsSE.py-|release|.zip) from the website link at the bottom the [WISDEM site](http://nwtc.nrel.gov/Turbine_CostsSE).

Install Turbine_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module from within an activated OpenMDAO environment:

	$ python
	> import turbine_costsse.turbine_costsse
	> import turbine_costsse.nrel_csm_tcc
        > import turbine_costsse.turbine_costsse_2015
        > import turbine_costsse.nrel_csm_tcc_2015

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

	$ python src/test/test_Turbine_CostsSE.py
        $ python src/test/test_Turbine_CostsSE_gradients.py
        $ python src/test/test_turbine_costsse_2015.py

For software issues please use <https://github.com/WISDEM/Turbine_CostsSE/issues>.  For functionality and theory related questions and comments please use the NWTC forum for [Systems Engineering Software Questions](https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002).

