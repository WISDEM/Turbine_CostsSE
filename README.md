# Turbine_CostsSE

Turbine_CostsSE is a set of models for assessing the costs of a wind turbine.  The first model is a new version of NREL's turbine Cost and Scaling Model that uses 2015 survey data to compute component mass properties from key turbine parameters such as rotor diameter, rated power and hub height.  A second model is a new mass-to-cost model which takes the individual component masses as inputs to estimate each component costs with additional cost factors for assembly, overhead, and profits.

Author: [NREL WISDEM Team](mailto:systems.engineering@nrel.gov) 

## Documentation

See local documentation in the `docs`-directory or access the online version at <http://wisdem.github.io/Turbine_CostsSE/>

## Installation

For detailed installation instructions of WISDEM modules see <https://github.com/WISDEM/WISDEM> or to install this Turbine_CostsSE by itself:

    $ python setup.py install

## Run Unit Tests

To check if installation was successful try to import the package:

	$ python
        > import turbine_costsse.turbine_costsse_2015
        > import turbine_costsse.nrel_csm_tcc_2015

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

        $ python src/test/test_turbine_costsse_2015.py

For software issues please use <https://github.com/WISDEM/Turbine_CostsSE/issues>.  For functionality and theory related questions and comments please use the NWTC forum for [Systems Engineering Software Questions](https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002).

