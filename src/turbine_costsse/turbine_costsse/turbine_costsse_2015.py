"""
turbine_costsse_2015.py

Created by Janine Freeman 2015 based on turbine_costsse.py 2012.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int, Enum
import numpy as np

from fusedwind.plant_cost.fused_tcc import FullTurbineCostModel, FullTCCAggregator, configure_full_tcc
from fusedwind.interface import implement_base

from rotor_costsse import Rotor_CostsSE_2015
from nacelle_costsse import Nacelle_CostsSE_2015
from tower_costsse import Tower_CostsSE_2015

#-------------------------------------------------------------------------------
@implement_base(FullTurbineCostModel)
class Turbine_CostsSE_2015(Assembly):

    # variables
	blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	blade_mass_cost_coeff = Float(13.08, iotype='in', units='$/kg', desc='blade mass-cost coefficient [$/kg]')
	hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	hub_mass_cost_coeff = Float(3.80, iotype='in', units='$/kg', desc='hub mass-cost coefficient [$/kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	pitch_system_mass_cost_coeff = Float(22.91, iotype='in', units='$/kg', desc='pitch system mass-cost coefficient [$/kg']) #mass-cost coefficient with default from list
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	spinner_mass_cost_coeff = Float(23.00, iotype='in', units='$/kg', desc='spinner/nose cone mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
	low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	lss_mass_cost_coeff = Float(12.60, iotype='in', units='$/kg', desc='low speed shaft mass-cost coefficient [$/kg]')
	main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
	number_main_bearings = Float(2, iotype='in', desc='number of main bearings []') #number of main bearings- defaults to 2
	bearings_mass_cost_coeff = Float(6.35, iotype='in', units='$/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings	
	gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass_cost_coeff = Float(17.40, iotype='in', units='$/kg', desc='gearbox mass-cost coefficient [$/kg]')
	high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	high_speed_side_mass_cost_coeff = Float(8.25, iotype='in', units='$/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
	generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    generator_mass_cost_coeff = Float(17.43, iotype='in', units= '$/kg', desc='generator mass cost coefficient [$/kg]')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	bedplate_mass_cost_coeff = Float(4.50, iotype='in', units='$/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	yaw_system_mass_cost_coeff = Float(11.01, iotype='in', units='$/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    variable_speed_elec_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='$/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    hydraulic_cooling_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	hydraulic_cooling_mass_cost_coeff = Float(163.95, iotype='in', units='$/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
	nacelle_cover_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	nacelle_cover_mass_cost_coeff = Float(7.61, iotype='in', units='$/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
	machine_rating = Float(iotype='in', units='kW', desc='machine rating')
	elec_connec_cost_esc = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for electrical connections') ####KLD update this
	elec_connec_machine_rating_cost_coeff = (40.0, iotype='in', units='$/kW', desc='2002 electrical connections cost coefficient per kW')
    offshore = Bool(iotype='in', desc='flag for offshore project')
	controls_cost_base = Array(np.array([35000.0,55900.0]), iotype='in', desc='2002 controls cost for [onshore, offshore]')
	controls_escalator = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for controls') ####KLD update this
	nacelle_platforms_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	nacelle_platforms_mass_cost_coeff = Float(8.7, iotype='in', units='$/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
	crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
	base_hardware_cost_coeff = Float(0.7, iotype='in', units='$/$', desc='base hardware cost coefficient based on bedplate cost [$/$]') #default from old CSM
    transformer_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= '$/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    tower_cost = Float(iotype='in', units='USD', desc='component cost')

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
	
	#multipliers
	rotor_assemblyCostMultiplier = Float(0.0, iotype='in', desc='rotor assembly cost multiplier')
	rotor_overheadCostMultiplier = Float(0.0, iotype='in', desc='rotor overhead cost multiplier')
    rotor_profitMultiplier = Float(0.0, iotype='in', desc='rotor profit multiplier')
    rotor_transportMultiplier = Float(0.0, iotype='in', desc='rotor transport multiplier')
	nacelle_assemblyCostMultiplier = Float(0.0, iotype='in', desc='nacelle assembly cost multiplier')
	nacelle_overheadCostMultiplier = Float(0.0, iotype='in', desc='nacelle overhead cost multiplier')
    nacelle_profitMultiplier = Float(0.0, iotype='in', desc='nacelle profit multiplier')
    nacelle_transportMultiplier = Float(0.0, iotype='in', desc='nacelle transport multiplier')
	tower_assemblyCostMultiplier = Float(0.0, iotype='in', desc='tower assembly cost multiplier')
	tower_overheadCostMultiplier = Float(0.0, iotype='in', desc='tower overhead cost multiplier')
	tower_profitMultiplier = Float(0.0, iotype='in', desc='tower profit cost multiplier')
	tower_transportMultiplier = Float(0.0, iotype='in', desc='tower transport cost multiplier')
    turbine_assemblyCostMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for assembly cost in manufacturing')
    turbine_overheadCostMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for overhead')
    turbine_profitMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for profit markup')
    turbine_transportMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for transport costs')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def configure(self):

        configure_full_tcc(self)

        # select components
        self.replace('rotorCC', Rotor_CostsSE_2015())
        self.replace('nacelleCC', Nacelle_CostsSE_2015())
        self.replace('towerCC', Tower_CostsSE_2015())
        self.replace('tcc', TurbineCostAdder2015())

        # connect inputs
        self.connect('blade_mass', 'rotorCC.blade_mass')
		self.connect('blade_mass_cost_coeff', 'rotorCC.blade_mass_cost_coeff')
        self.connect('hub_mass', 'rotorCC.hub_mass')
		self.connect('hub_mass_cost_coeff', 'rotorCC.hub_mass_cost_coeff')
        self.connect('pitch_system_mass', 'rotorCC.pitch_system_mass')
		self.connect('pitch_system_mass_cost_coeff', 'rotorCC.pitch_system_mass_cost_coeff')
        self.connect('spinner_mass', 'rotorCC.spinner_mass')
		self.connect('spinner_mass_cost_coeff', 'rotorCC.spinner_mass_cost_coeff')
        self.connect('blade_number', 'rotorCC.blade_number')
        self.connect('low_speed_shaft_mass', 'nacelleCC.low_speed_shaft_mass')
		self.connect('lss_mass_cost_coeff', 'nacelleCC.lss_mass_cost_coeff')
        self.connect('main_bearing_mass', 'nacelleCC.main_bearing_mass')
		self.connect('number_main_bearings', 'nacelleCC.number_main_bearings')
        self.connect('bearings_mass_cost_coeff', 'nacelleCC.bearings_mass_cost_coeff')
        self.connect('gearbox_mass', 'nacelleCC.gearbox_mass')
		self.connect('gearbox_mass_cost_coeff', 'nacelleCC.gearbox_mass_cost_coeff')
		self.connect('high_speed_side_mass', 'nacelleCC.high_speed_side_mass')
		self.connect('high_speed_side_mass_cost_coeff', 'nacelleCC.high_speed_side_mass_cost_coeff')
        self.connect('generator_mass', 'nacelleCC.generator_mass')
		self.connect('generator_mass_cost_coeff', 'nacelleCC.generator_mass_cost_coeff')
        self.connect('bedplate_mass', 'nacelleCC.bedplate_mass')
		self.connect('bedplate_mass_cost_coeff', 'nacelleCC.bedplate_mass_cost_coeff')
        self.connect('yaw_system_mass', 'nacelleCC.yaw_system_mass')
		self.connect('yaw_system_mass_cost_coeff', 'nacelleCC.yaw_system_mass_cost_coeff')
		self.connect('variable_speed_elec_mass', 'nacelleCC.variable_speed_elec_mass')
		self.connect('variable_speed_elec_mass_cost_coeff', 'nacelleCC.variable_speed_elec_mass_cost_coeff')
		self.connect('hydraulic_cooling_mass', 'nacelleCC.hydraulic_cooling_mass')
		self.connect('hydraulic_cooling_mass_cost_coeff', 'nacelleCC.hydraulic_cooling_mass_cost_coeff')
		self.connect('nacelle_cover_mass', 'nacelleCC.nacelle_cover_mass')
		self.connect('nacelle_cover_mass_cost_coeff', 'nacelleCC.nacelle_cover_mass_cost_coeff')
		self.connect('machine_rating','nacelleCC.machine_rating')
		self.connect('elec_connec_cost_esc', 'nacelleCC.elec_connec_cost_esc')
		self.connect('elec_connec_machine_rating_cost_coeff', 'nacelleCC.elec_connec_machine_rating_cost_coeff')
		self.connect('offshore', 'nacelleCC.offshore')
		self.connect('controls_cost_base', 'nacelleCC.controls_cost_base')
		self.connect('controls_escalator', 'nacelleCC.controls_escalator')
		self.connect('nacelle_platforms_mass', 'nacelleCC.nacelle_platforms_mass')
		self.connect('nacelle_platforms_mass_cost_coeff', 'nacelleCC.nacelle_platforms_mass_cost_coeff')
		self.connect('crane', 'nacelleCC.crane')
		self.connect('crane_cost', 'nacelleCC.crane_cost')
		self.connect('bedplate_cost', 'nacelleCC.bedplate_cost')
		self.connect('base_hardware_cost_coeff', 'nacelleCC.base_hardware_cost_coeff')
		self.connect('transformer_mass', 'nacelleCC.transformer_mass')
		self.connect('transformer_mass_cost_coeff', 'nacelleCC.transformer_mass_cost_coeff')
        self.connect('tower_mass', 'towerCC.tower_mass')
        
		# connect multipliers
		self.connect('rotor_assemblyCostMultiplier', 'rotorCC.rotor_assemblyCostMultiplier')
		self.connect('rotor_overheadCostMultiplier' 'rotorCC.rotor_overheadCostMultiplier')
		self.connect('rotor_profitMultiplier', 'rotorCC.rotor_profitMultiplier')
		self.connect('rotor_transportMultiplier', 'rotorCC.rotor_transportMultiplier')
		self.connect('nacelle_assemblyCostMultiplier', 'nacelleCC.nacelle_assemblyCostMultiplier')
		self.connect('nacelle_overheadCostMultiplier' 'nacelleCC.nacelle_overheadCostMultiplier')
		self.connect('nacelle_profitMultiplier', 'nacelleCC.nacelle_profitMultiplier')
		self.connect('nacelle_transportMultiplier', 'nacelleCC.nacelle_transportMultiplier')
		self.connect('tower_assemblyCostMultiplier', 'towerCC.tower_assemblyCostMultiplier')
		self.connect('tower_overheadCostMultiplier' 'towerCC.tower_overheadCostMultiplier')
		self.connect('tower_profitMultiplier', 'towerCC.tower_profitMultiplier')
		self.connect('tower_transportMultiplier', 'towerCC.tower_transportMultiplier')
		self.connect('turbine_assemblyCostMultiplier', 'tcc.turbine_assemblyCostMultiplier')
		self.connect('turbine_overheadCostMultiplier', 'tcc.turbine_overheadCostMultiplier')
		self.connect('turbine_profitMultiplier', 'tcc.turbine_profitMultiplier')
		self.connect('turbine_transportMultiplier', 'tcc.turbine_transportMultiplier')


#-------------------------------------------------------------------------------
@implement_base(FullTCCAggregator)
class TurbineCostAdder2015(Component):

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # parameters
    turbine_assemblyCostMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for assembly cost in manufacturing')
    turbine_overheadCostMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for overhead')
    turbine_profitMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for profit markup')
    turbine_transportMultiplier = Float(0.0, iotype='in', desc='turbine multiplier for transport costs')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def __init__(self):

        Component.__init__(self)

    def execute(self):

        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        self.turbine_cost = (1 + self.turbine_transportMultiplier + self.turbine_profitMultiplier) * ((1 + self.turbine_overheadCostMultiplier + self.turbine_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------

def example():

    # simple test of module

    turbine = Turbine_CostsSE()

    turbine.blade_mass = 17650.67  # inline with the windpact estimates
    turbine.hub_mass = 31644.5
    turbine.pitch_system_mass = 17004.0
    turbine.spinner_mass = 1810.5
    turbine.low_speed_shaft_mass = 31257.3
    #bearingsMass = 9731.41
    turbine.main_bearing_mass = 9731.41 / 2
    turbine.second_bearing_mass = 9731.41 / 2
    turbine.gearbox_mass = 30237.60
    turbine.high_speed_side_mass = 1492.45
    turbine.generator_mass = 16699.85
    turbine.bedplate_mass = 93090.6
    turbine.yaw_system_mass = 11878.24
    turbine.tower_mass = 434559.0
    turbine.machine_rating = 5000.0
    turbine.advanced = True
    turbine.blade_number = 3
    turbine.drivetrain_design = 'geared'
    turbine.crane = True
    turbine.offshore = True
    turbine.year = 2010
    turbine.month =  12

    turbine.run()

    print "The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:"
    print
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(turbine.rotorCC.cost)
    print "Blade cost is ${0:.2f} USD".format(turbine.rotorCC.bladeCC.cost)
    print "Hub cost is ${0:.2f} USD".format(turbine.rotorCC.hubCC.cost)
    print "Pitch system cost is ${0:.2f} USD".format(turbine.rotorCC.pitchSysCC.cost)
    print "Spinner cost is ${0:.2f} USD".format(turbine.rotorCC.spinnerCC.cost)
    print
    print "Overall nacelle cost is ${0:.2f} USD".format(turbine.nacelleCC.cost)
    print "LSS cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "Main bearings cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "Gearbox cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "High speed side cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "Generator cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "Bedplate cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print "Yaw system cost is ${0:.2f} USD".format(turbine.nacelleCC.nacelleCC.cost)
    print
    print "Tower cost is ${0:.2f} USD".format(turbine.towerCC.cost)
    print
    print "The overall turbine cost is ${0:.2f} USD".format(turbine.turbine_cost)
    print

if __name__ == "__main__":

    example()