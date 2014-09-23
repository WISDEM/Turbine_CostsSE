Turbine_CostsSE is a set of models for assessing the costs of a wind turbine.  The first model is based on the NREL Cost and Scaling Model which uses component mass information as well as key turbine parameters such as rotor diameter, rated power and hub height to cost out the whole turbine.  A second model is a new mass-to-cost model which takes the individual component masses as inputs to estimate each component costs with additional cost factors for assembly, overhead, and profits.

Author: [K. Dykes](mailto:katherine.dykes@nrel.gov)

## Detailed Documentation

For detailed documentation see <http://wisdem.github.io/Turbine_CostsSE/>

## Prerequisites

NumPy, SciPy, FUSED-Wind, OpenMDAO

## Installation

Install Turbine_CostsSE within an activated OpenMDAO environment

	$ plugin install

It is not recommended to install the software outside of OpenMDAO.

## Run Unit Tests

To check if installation was successful try to import the module

	$ python
	> import turbine_costsse.turbine_costsse.turbine_costsse
	> import turbine_costsse.nrel_csm_tcc.nrel_csm_tcc

You may also run the unit tests which include functional and gradient tests.  Analytic gradients are provided for variables only so warnings will appear for missing gradients on model input parameters; these can be ignored.

	$ python src/test/test_Turbine_CostsSE.py

For software issues please use <https://github.com/WISDEM/Turbine_CostsSE/issues>.  For functionality and theory related questions and comments please use the NWTC forum for [Systems Engineering Software Questions]<https://wind.nrel.gov/forum/wind/viewtopic.php?f=34&t=1002>.

