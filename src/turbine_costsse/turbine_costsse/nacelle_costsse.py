"""
nacelle_costsse.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from commonse.config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int, Enum
from math import pi
import numpy as np

from fusedwind.plant_cost.fused_tcc import FullNacelleCostModel, BaseComponentCostModel, FullNacelleCostAggregator, configure_full_ncc
from fusedwind.interface import implement_base

# -------------------------------------------------
@implement_base(BaseComponentCostModel) #pre-check for fusedwind that inputs/outputs are as expected, should precede every cost model
class LowSpeedShaftCost(Component):

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine low speed shaft component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        # calculate component cost
        LowSpeedShaftCost2002 = 3.3602 * self.low_speed_shaft_mass + 13587      # equation adjusted to be based on mass rather than rotor diameter using data from CSM
        lowSpeedShaftCostEsc            = ppi.compute('IPPI_LSS')
        self.cost = (LowSpeedShaftCost2002 * lowSpeedShaftCostEsc )

        # derivatives
        self.d_cost_d_low_speed_shaft_mass = lowSpeedShaftCostEsc * 3.3602

    def list_deriv_vars(self):

        inputs = ['low_speed_shaft_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_low_speed_shaft_mass]])

        return self.J

# -------------------------------------------------
@implement_base(BaseComponentCostModel)
class LowSpeedShaftCost2015(Component):

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
	lss_mass_cost_coeff = Float(12.60, iotype='in', units='$/kg', desc='low speed shaft mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs') #initialize cost output

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine low speed shaft component.

        '''

        Component.__init__(self)

    def execute(self):

        # calculate component cost
        LowSpeedShaftCost2015 = self.lss_mass_cost_coeff * self.low_speed_shaft_mass
		self.cost = LowSpeedShaftCost2015 #assign the cost to this object so don't have to return anything

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BearingsCost(Component):

    # variables
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine maing bearings.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month
        bearingsMass = self.main_bearing_mass + self.second_bearing_mass

        # calculate component cost
        bearingCostEsc       = ppi.compute('IPPI_BRN')

        brngSysCostFactor = 17.6 # $/kg                  # cost / unit mass from CSM
        Bearings2002 = (bearingsMass) * brngSysCostFactor
        self.cost    = (( Bearings2002 ) * bearingCostEsc ) / 4   # div 4 to account for bearing cost mass differences CSM to Sunderland

        # derivatives
        self.d_cost_d_main_bearing_mass = bearingCostEsc * brngSysCostFactor / 4
        self.d_cost_d_second_bearing_mass = bearingCostEsc * brngSysCostFactor / 4

    def list_deriv_vars(self):

        inputs = ['main_bearing_mass', 'second_bearing_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_main_bearing_mass, self.d_cost_d_second_bearing_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BearingsCost2015(Component):

    # variables
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
	number_main_bearings = Float(2, iotype='in', desc='number of main bearings []') #number of main bearings- defaults to 2
	bearings_mass_cost_coeff = Float(6.35, iotype='in', units='$/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine main bearings.

        '''

        Component.__init__(self)

    def execute(self):
		
		#calculate component cost
        BearingsCost2015 = self.bearings_mass_cost_coeff * self.main_bearing_mass * self.number_main_bearings
		self.cost = BearingsCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GearboxCost(Component):

    # variables
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')

    # parameters
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        # calculate component cost
        GearboxCostEsc     = ppi.compute('IPPI_GRB')

        costCoeff = [None, 16.45  , 74.101     ,   15.25697015,  0 ]
        costExp   = [None,  1.2491,  1.002     ,    1.2491    ,  0 ]

        if self.drivetrain_design == 'geared':
            drivetrain_design = 1
        elif self.drivetrain_design == 'single_stage':
            drivetrain_design = 2
        elif self.drivetrain_design == 'multi-drive':
            drivetrain_design = 3
        elif self.drivetrain_design == 'pm_direct_drive':
            drivetrain_design = 4

        if drivetrain_design == 1:
          Gearbox2002 = 16.9 * self.gearbox_mass - 25066          # for traditional 3-stage gearbox, use mass based cost equation from NREL CSM
        else:
          Gearbox2002 = costCoeff[drivetrain_design] * (self.machine_rating ** costCoeff[drivetrain_design])        # for other drivetrain configurations, use NREL CSM equation based on machine rating

        self.cost   = Gearbox2002 * GearboxCostEsc

        # derivatives
        if drivetrain_design == 1:
          self.d_cost_d_gearbox_mass = GearboxCostEsc * 16.9
          self.d_cost_d_machine_rating = 0.0
        else:
          self.d_cost_d_gearbox_mass = 0.0
          self.d_cost_d_machine_rating =  GearboxCostEsc * costCoeff[drivetrain_design] * (costCoeff[drivetrain_design] * (self.machine_rating ** (costCoeff[drivetrain_design]-1)))

    def list_deriv_vars(self):

        inputs= ['gearbox_mass', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        self.J = np.array([[self.d_cost_d_gearbox_mass, self.d_cost_d_machine_rating]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GearboxCost2015(Component):

    # variables
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass_cost_coeff = Float(17.40, iotype='in', units='$/kg', desc='gearbox mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.

        '''

        Component.__init__(self)

    def execute(self):

        # calculate component cost
		GearboxCost2015 = self.gearbox_mass_cost_coeff * self.gearbox_mass
		self.cost = GearboxCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HighSpeedSideCost(Component):

    # variables
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine mechanical brake and HSS component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month
        # calculate component cost
        mechBrakeCostEsc     = ppi.compute('IPPI_BRK')
        mechBrakeCost2002    = 10 * self.high_speed_side_mass                  # mechanical brake system cost based on $10 / kg multiplier from CSM model (inverse relationship)
        self.cost            = mechBrakeCostEsc * mechBrakeCost2002

        # derivatives
        self.d_cost_d_high_speed_side_mass = mechBrakeCostEsc * 10

    def list_deriv_vars(self):

        inputs = ['high_speed_side_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_high_speed_side_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HighSpeedSideCost2015(Component):

    # variables
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	high_speed_side_mass_cost_coeff = Float(8.25, iotype='in', units='$/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine mechanical brake and HSS component.

        '''

        Component.__init__(self)

    def execute(self):

        # calculate component cost
        MechBrakeCost2015 = self.high_speed_side_mass_cost_coeff * self.high_speed_side_mass
        self.cost = MechBrakeCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GeneratorCost(Component):

    # variables
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')

    # parameters
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine generator component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        # calculate component cost                                      #TODO: only handles traditional drivetrain configuration at present
        generatorCostEsc     = ppi.compute('IPPI_GEN')
        costCoeff = [None, 65    , 54.73 ,  48.03 , 219.33 ] # $/kW - from 'Generators' worksheet

        if self.drivetrain_design == 'geared':
            drivetrain_design = 1
        elif self.drivetrain_design == 'single_stage':
            drivetrain_design = 2
        elif self.drivetrain_design == 'multi-drive':
            drivetrain_design = 3
        elif self.drivetrain_design == 'pm_direct_drive':
            drivetrain_design = 4

        if drivetrain_design == 1:
            GeneratorCost2002 = 19.697 * self.generator_mass + 9277.3
        else:
            GeneratorCost2002 = costCoeff[drivetrain_design] * self.machine_rating

        self.cost         = GeneratorCost2002 * generatorCostEsc

        # derivatives
        if drivetrain_design == 1:
            self.d_cost_d_generator_mass = generatorCostEsc * 19.697
            self.d_cost_d_machine_rating = 0.0
        else:
            self.d_cost_d_generator_mass = 0.0
            self.d_cost_d_machine_rating = costCoeff[drivetrain_design] * generatorCostEsc

    def list_deriv_vars(self):

        inputs = ['generator_mass', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_generator_mass, self.d_cost_d_machine_rating]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GeneratorCost2015(Component):

    # variables
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    generator_mass_cost_coeff = Float(17.43, iotype='in', units= '$/kg', desc='generator mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine generator component.

        '''

        Component.__init__(self)

    def execute(self):

        #calculate component cost
		GeneratorCost2015 = self.generator_mass_cost_coeff * self.generator_mass
		self.cost = GeneratorCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BedplateCost(Component):

    # variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')
    drivetrain_design = Int(iotype='in', desc='type of drivetrain')

    # Outputs
    cost2002 = Float(iotype='out', units='USD', desc='component cost in 2002 USD')
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine bedplate component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate component cost                                    # TODO: cost needs to be adjusted based on look-up table or a materials, mass and manufacturing equation
        BedplateCostEsc     = ppi.compute('IPPI_MFM')

        #TODO: handle different drivetrain types
        costCoeff = [None, 9.48850 , 303.96000, 17.92300 , 627.280000 ]
        costExp   = [None, 1.9525, 1.0669, 1.6716, 0.85]

        self.cost2002 = 0.9461 * self.bedplate_mass + 17799                   # equation adjusted based on mass / cost relationships for components documented in NREL CSM
        self.cost     = self.cost2002 * BedplateCostEsc

        # derivatives
        self.d_cost_d_bedplate_mass = BedplateCostEsc * 0.9461
        self.d_cost2002_d_bedplate_mass = 0.9461

    def list_deriv_vars(self):

        inputs = ['bedplate_mass']
        outputs = ['cost', 'cost2002']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_bedplate_mass], [self.d_cost2002_d_bedplate_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BedplateCost2015(Component):

    # variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	bedplate_mass_cost_coeff = Float(4.50, iotype='in', units='$/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine bedplate component.

        '''

        Component.__init__(self)

    def execute(self):

        # calculate component cost
		BedplateCost2015 = self.bedplate_mass_cost_coeff * self.bedplate_mass
		self.cost = BedplateCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class YawSystemCost(Component):

    # variables
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        # calculate component cost
        yawDrvBearingCostEsc = ppi.compute('IPPI_YAW')

        YawDrvBearing2002 = 8.3221 * self.yaw_system_mass + 2708.5          # cost / mass relationship derived from NREL CSM data
        self.cost         = YawDrvBearing2002 * yawDrvBearingCostEsc

        # derivatives
        self.d_cost_d_yaw_system_mass = yawDrvBearingCostEsc * 8.3221

    def list_deriv_vars(self):

        inputs = ['yaw_system_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_yaw_system_mass]])

        return self.J

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class YawSystemCost2015(Component):

    # variables
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	yaw_system_mass_cost_coeff = Float(11.01, iotype='in', units='$/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        # calculate cost
		YawSystemCost2015 = self.yaw_system_mass_cost_coeff * self.yaw_system_mass
        self.cost = YawSystemCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class VariableSpeedElecCost2015(Component):

    # variables
    variable_speed_elec_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='$/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        # calculate cost
		VariableSpeedElecCost2015 = self.variable_speed_elec_mass_cost_coeff * self.variable_speed_elec_mass
        self.cost = VariableSpeedElecCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HydraulicCoolingCost2015(Component):

    # variables
    hydraulic_cooling_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	hydraulic_cooling_mass_cost_coeff = Float(163.95, iotype='in', units='$/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        # calculate cost
		HydraulicCoolingCost2015 = self.hydraulic_cooling_mass_cost_coeff * self.hydraulic_cooling_mass
        self.cost = HydraulicCoolingCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class NacelleCoverCost2015(Component):

    # variables
    nacelle_cover_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	nacelle_cover_mass_cost_coeff = Float(7.61, iotype='in', units='$/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        # calculate cost
		NacelleCoverCost2015 = self.nacelle_cover_mass_cost_coeff * self.nacelle_cover_mass
        self.cost = NacelleCoverCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class ElecConnecCost2015(Component):

    # variables
	machine_rating = Float(iotype='in', units='kW', desc='machine rating')
	elec_connec_cost_esc = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for electrical connections') ####KLD update this
	elec_connec_machine_rating_cost_coeff = (40.0, iotype='in', units='$/kW', desc='2002 electrical connections cost coefficient per kW') #default from old CSM

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        # electronic systems, hydraulics and controls
        ElecConnecCost2015  = self.elec_connec_machine_rating_cost_coeff * self.machine_rating * self.elec_connec_cost_esc #escalator will be from 2002 $ to 2015 $
        self.cost = ElecConnecCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class ControlsCost2015(Component):

    # variables
    offshore = Bool(iotype='in', desc='flag for offshore project')
	controls_cost_base = Array(np.array([35000.0,55900.0]), iotype='in', desc='2002 controls cost for [onshore, offshore]') #defaults from old CSM
	controls_escalator = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for controls') ####KLD update this

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

        if (not self.offshore):
			ControlsCost = self.controls_cost_base[0] * self.controls_escalator
        else:
			ControlsCost  = self.controls_cost_base[1] * self.controls_escalator
		self.cost = ControlsCost

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class OtherMainframeCost2015(Component):

	#model all three (nacelle platform, service crane, and base hardware) from old model, DO NOT USE THE COST/KG IN THE LIST
	
    # variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
	nacelle_platforms_mass_coeff = Float(0.125, iotype='in', units='kg/kg', desc='nacelle platforms mass coefficient as a function of bedplate mass [kg/kg]') #default from old CSM
	nacelle_platforms_mass_cost_coeff = Float(8.7, iotype='in', units='$/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
	crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
	base_hardware_cost_coeff = Float(0.7, iotype='in', units='$/$', desc='base hardware cost coefficient based on bedplate cost [$/$]') #default from old CSM

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine yaw system.
        '''
        
        Component.__init__(self)

    def execute(self):

	    # nacelle platform cost
        nacellePlatformsMass = self.nacelle_platforms_mass_coeff * self.bedplate_mass
        NacellePlatformsCost = self.nacelle_platforms_mass_cost_coeff * nacellePlatformsMass

		# crane cost
        if (self.crane):
            craneCost  = self.crane_cost
        else:
            craneCost  = 0.0

        # base hardware cost
        BaseHardwareCost = self.bedplate_cost * self.base_hardware_cost_coeff
		
		#aggregate all three mainframe costs
        MainFrameCost = (NacellePlatformsCost + craneCost + BaseHardwareCost)
        self.cost  = MainFrameCost

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class TransformerCost2015(Component):

    # variables
    transformer_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= '$/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine generator component.

        '''

        Component.__init__(self)

    def execute(self):

        #calculate component cost
		TransformerCost2015 = self.transformer_mass_cost_coeff * self.transformer_mass
		self.cost = TransformerCost2015

#-------------------------------------------------------------------------------
@implement_base(FullNacelleCostAggregator)
class NacelleSystemCostAdder(Component):

    # variables
    lss_cost = Float(iotype='in', units='USD', desc='component cost')
    bearings_cost = Float(iotype='in', units='USD', desc='component cost')
    gearbox_cost = Float(iotype='in', units='USD', desc='component cost')
    hss_cost = Float(iotype='in', units='USD', desc='component cost')
    generator_cost = Float(iotype='in', units='USD', desc='component cost')
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost')
    yaw_system_cost = Float(iotype='in', units='USD', desc='component cost')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
    bedplateCost2002 = Float(iotype='in', units='USD', desc='component cost in 2002 USD')

    # parameters
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore project')
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.
        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        BedplateCostEsc      = ppi.compute('IPPI_MFM')

        # mainframe system including bedplate, platforms, crane and miscellaneous hardware
        nacellePlatformsMass = 0.125 * self.bedplate_mass
        NacellePlatforms2002 = 8.7 * nacellePlatformsMass

        if (self.crane):
            craneCost2002  = 12000.0
        else:
            craneCost2002  = 0.0

        # aggregation of mainframe components: bedplate, crane and platforms into single mass and cost
        BaseHardwareCost2002  = self.bedplateCost2002 * 0.7 #use this fraction but updated bedplate cost
        MainFrameCost2002   = (NacellePlatforms2002 + craneCost2002  + \
                          BaseHardwareCost2002 )
        self.mainframe_cost  = MainFrameCost2002 * BedplateCostEsc + self.bedplate_cost

        # calculations of mass and cost for other systems not included above as main drivetrain load-bearing components
        # Cost Escalators - should be obtained from PPI tables
        VspdEtronicsCostEsc  = ppi.compute('IPPI_VSE')
        nacelleCovCostEsc    = ppi.compute('IPPI_NAC')
        hydrCoolingCostEsc   = ppi.compute('IPPI_HYD')
        econnectionsCostEsc  = ppi.compute('IPPI_ELC')
        controlsCostEsc      = ppi.compute('IPPI_CTL')

        # electronic systems, hydraulics and controls
        econnectionsCost2002  = 40.0 * self.machine_rating  # 2002
        self.econnectionsCost = econnectionsCost2002 * econnectionsCostEsc

        VspdEtronics2002      = 79.32 * self.machine_rating
        self.vspdEtronicsCost = VspdEtronics2002 * VspdEtronicsCostEsc

        hydrCoolingCost2002  = 12.0 * self.machine_rating # 2002
        self.hydrCoolingCost = hydrCoolingCost2002 * hydrCoolingCostEsc

        if (not self.offshore):
            ControlsCost2002  = 35000.0 # initial approximation 2002
            self.controlsCost = ControlsCost2002 * controlsCostEsc
        else:
            ControlsCost2002  = 55900.0 # initial approximation 2002
            self.controlsCost = ControlsCost2002 * controlsCostEsc

        nacelleCovCost2002  = 11.537 * self.machine_rating + (3849.7)
        self.nacelleCovCost = nacelleCovCost2002 * nacelleCovCostEsc

        # aggregation of nacelle costs
        partsCost = self.lss_cost + \
                    self.bearings_cost + \
                    self.gearbox_cost + \
                    self.hss_cost + \
                    self.generator_cost + \
                    self.mainframe_cost + \
                    self.yaw_system_cost + \
                    self.econnectionsCost + \
                    self.vspdEtronicsCost + \
                    self.hydrCoolingCost + \
                    self.controlsCost + \
                    self.nacelleCovCost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        # derivatives
        self.d_cost_d_bedplate_mass = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier) * BedplateCostEsc * 8.7 * 0.125
        self.d_cost_d_bedplateCost2002 = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier) * BedplateCostEsc * 0.7
        self.d_cost_d_bedplateCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_lowSpeedShaftCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_bearingsCost= (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_gearboxCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_highSpeedSideCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_generatorCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_yawSystemCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_machine_rating = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier) * \
                                 (econnectionsCostEsc * 40.0 + VspdEtronicsCostEsc * 79.32 + hydrCoolingCostEsc * 12.0 + nacelleCovCostEsc * 11.537))

    def list_deriv_vars(self):

        inputs = ['bedplate_mass', 'bedplateCost2002', 'bedplate_cost', 'lss_cost', 'bearings_cost', \
                      'gearbox_cost', 'hss_cost', 'generator_cost', 'yaw_system_cost', 'machine_rating']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_bedplate_mass, self.d_cost_d_bedplateCost2002, self.d_cost_d_bedplateCost, \
                            self.d_cost_d_lowSpeedShaftCost, self.d_cost_d_bearingsCost, self.d_cost_d_gearboxCost, \
                            self.d_cost_d_highSpeedSideCost, self.d_cost_d_generatorCost, \
                            self.d_cost_d_yawSystemCost, self.d_cost_d_machine_rating]])

        return self.J

#------------------------------------------------------------------
class Nacelle_CostsSE(FullNacelleCostModel):

    '''
       Nacelle_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass')
    generator_mass = Float(iotype='in', units='kg', desc='component mass')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')

    # parameters
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flat for offshore site')
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # outputs
    cost = Float(iotype='out', units='USD', desc='component cost')

    def configure(self):

        configure_full_ncc(self)

        # select components
        self.replace('lssCC', LowSpeedShaftCost())
        self.replace('bearingsCC', BearingsCost())
        self.replace('gearboxCC', GearboxCost())
        self.replace('hssCC', HighSpeedSideCost())
        self.replace('generatorCC', GeneratorCost())
        self.replace('bedplateCC', BedplateCost())
        self.replace('yawSysCC', YawSystemCost())
        self.replace('ncc', NacelleSystemCostAdder())

        # connect inputs
        self.connect('low_speed_shaft_mass', 'lssCC.low_speed_shaft_mass')
        self.connect('main_bearing_mass', 'bearingsCC.main_bearing_mass')
        self.connect('second_bearing_mass', 'bearingsCC.second_bearing_mass')
        self.connect('gearbox_mass', 'gearboxCC.gearbox_mass')
        self.connect('high_speed_side_mass', 'hssCC.high_speed_side_mass')
        self.connect('generator_mass', 'generatorCC.generator_mass')
        self.connect('bedplate_mass', ['bedplateCC.bedplate_mass', 'ncc.bedplate_mass'])
        self.connect('yaw_system_mass', 'yawSysCC.yaw_system_mass')
        self.connect('machine_rating', ['gearboxCC.machine_rating', 'ncc.machine_rating'])
        self.connect('drivetrain_design', ['gearboxCC.drivetrain_design', 'generatorCC.drivetrain_design'])
        self.connect('crane', 'ncc.crane')
        self.connect('offshore', 'ncc.offshore')
        self.connect('year', ['lssCC.year', 'bearingsCC.year', 'gearboxCC.year', 'hssCC.year', 'generatorCC.year', 'bedplateCC.year', 'yawSysCC.year', 'ncc.year'])
        self.connect('month', ['lssCC.month', 'bearingsCC.month', 'gearboxCC.month', 'hssCC.month', 'generatorCC.month', 'bedplateCC.month', 'yawSysCC.month', 'ncc.month'])
        
        self.connect('bedplateCC.cost2002','ncc.bedplateCost2002')

#-------------------------------------------------------------------------------
@implement_base(FullNacelleCostAggregator)
class NacelleSystemCostAdder2015(Component):

    # variables
    lss_cost = Float(iotype='in', units='USD', desc='component cost')
    bearings_cost = Float(iotype='in', units='USD', desc='component cost')
    gearbox_cost = Float(iotype='in', units='USD', desc='component cost')
    hss_cost = Float(iotype='in', units='USD', desc='component cost')
    generator_cost = Float(iotype='in', units='USD', desc='component cost')
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost')
    yaw_system_cost = Float(iotype='in', units='USD', desc='component cost')
	variable_speed_elec_cost = Float(iotype='in', units='USD', desc='component cost')
	hydraulic_cooling_cost = Float(iotype='in', units='USD', desc='component cost')
	nacelle_cover_cost = Float(iotype='in', units='USD', desc='component cost')
	elec_connec_cost = Float(iotype='in', units='USD', desc='component cost')
	controls_cost = Float(iotype='in', units='USD', desc='component cost')
	other_mainframe_cost = Float(iotype='in', units='USD', desc='component cost')
	transformer_cost = Float(iotype='in', units='USD', desc='component cost')
	
	#multipliers
	assemblyCostMultiplier = Float(0.0, iotype='in', desc='cost multiplier for assembly')
	overheadCostMultiplier = Float(0.0, iotype='in', desc='cost multiplier for overhead')
    profitMultiplier = Float(0.0, iotype='in', desc='cost multiplier for profit')
    transportMultiplier = Float(0.0, iotype='in', desc='cost multiplier for transport')

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine gearbox component.
        '''

        Component.__init__(self)

    def execute(self):

        # aggregation of nacelle costs
        partsCost = self.lss_cost + \
                    self.bearings_cost + \
                    self.gearbox_cost + \
                    self.hss_cost + \
                    self.generator_cost + \
					self.bedplate_cost + \
                    self.yaw_system_cost + \
                    self.variable_speed_elec_cost + \
                    self.hydraulic_cooling_cost + \
                    self.nacelle_cover_cost + \
					self.elec_connec_cost + \
					self.controls_cost + \
					self.other_mainframe_cost + \
					self.transformer_cost

		#apply multipliers for assembly, transport, overhead, and profits
        self.cost = (1 + self.transportMultiplier + self.profitMultiplier) * ((1 + self.overheadCostMultiplier + self.assemblyCostMultiplier) * partsCost)

#---------------------------------------------------------------------------------------------
class Nacelle_CostsSE_2015(FullNacelleCostModel):

    '''
       Nacelle_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
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
	nacelle_platforms_mass_coeff = Float(0.125, iotype='in', units='kg/kg', desc='nacelle platforms mass coefficient as a function of bedplate mass [kg/kg]') #default from old CSM
	nacelle_platforms_mass_cost_coeff = Float(8.7, iotype='in', units='$/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
	crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
	base_hardware_cost_coeff = Float(0.7, iotype='in', units='$/$', desc='base hardware cost coefficient based on bedplate cost [$/$]') #default from old CSM
    transformer_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= '$/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
	
	#multipliers
	assemblyCostMultiplier = Float(0.0, iotype='in', desc='cost multiplier for assembly')
	overheadCostMultiplier = Float(0.0, iotype='in', desc='cost multiplier for overhead')
    profitMultiplier = Float(0.0, iotype='in', desc='cost multiplier for profit')
    transportMultiplier = Float(0.0, iotype='in', desc='cost multiplier for transport')

    # outputs
    cost = Float(iotype='out', units='USD', desc='component cost')

    def configure(self):

        configure_full_ncc(self)

        # select components #this creates an instance of each of these components with the name in ''
        self.replace('lssCC', LowSpeedShaftCost2015())
        self.replace('bearingsCC', BearingsCost2015())
        self.replace('gearboxCC', GearboxCost2015())
        self.replace('hssCC', HighSpeedSideCost2015())
        self.replace('generatorCC', GeneratorCost2015())
        self.replace('bedplateCC', BedplateCost2015())
        self.replace('yawSysCC', YawSystemCost2015())
		self.replace('vsCC', VariableSpeedElecCost2015())
		self.replace('hydraulicCC', HydraulicCoolingCost2015())
		self.replace('nacelleCC', NacelleCoverCost2015())
		self.replace('elecCC', ElecConnecCost2015())
		self.replace('controlsCC', ControlsCost2015())
		self.replace('mainframeCC', OtherMainframeCost2015())
		self.replace('transformerCC', TransformerCost2015())
	    self.replace('ncc', NacelleSystemCostAdder2015())

        # connect inputs
        self.connect('low_speed_shaft_mass', 'lssCC.low_speed_shaft_mass')
		self.connect('lss_mass_cost_coeff', 'lssCC.lss_mass_cost_coeff')
        self.connect('main_bearing_mass', 'bearingsCC.main_bearing_mass')
		self.connect('number_main_bearings', 'bearingsCC.number_main_bearings')
        self.connect('bearings_mass_cost_coeff', 'bearingsCC.bearings_mass_cost_coeff')
        self.connect('gearbox_mass', 'gearboxCC.gearbox_mass')
		self.connect('gearbox_mass_cost_coeff', 'gearboxCC.gearbox_mass_cost_coeff')
		self.connect('high_speed_side_mass', 'hssCC.high_speed_side_mass')
		self.connect('high_speed_side_mass_cost_coeff', 'hssCC.high_speed_side_mass_cost_coeff')
        self.connect('generator_mass', 'generatorCC.generator_mass')
		self.connect('generator_mass_cost_coeff', 'generatorCC.generator_mass_cost_coeff')
        self.connect('bedplate_mass', ['bedplateCC.bedplate_mass', 'mainframeCC.bedplate_mass'])
		self.connect('bedplate_mass_cost_coeff', 'bedplateCC.bedplate_mass_cost_coeff')
        self.connect('yaw_system_mass', 'yawSysCC.yaw_system_mass')
		self.connect('yaw_system_mass_cost_coeff', 'yawSysCC.yaw_system_mass_cost_coeff')
		self.connect('variable_speed_elec_mass', 'vsCC.variable_speed_elec_mass')
		self.connect('variable_speed_elec_mass_cost_coeff', 'vsCC.variable_speed_elec_mass_cost_coeff')
		self.connect('hydraulic_cooling_mass', 'hydraulicCC.hydraulic_cooling_mass')
		self.connect('hydraulic_cooling_mass_cost_coeff', 'hydraulicCC.hydraulic_cooling_mass_cost_coeff')
		self.connect('nacelle_cover_mass', 'nacelleCC.nacelle_cover_mass')
		self.connect('nacelle_cover_mass_cost_coeff', 'nacelleCC.nacelle_cover_mass_cost_coeff')
		self.connect('machine_rating','elecCC.machine_rating')
		self.connect('elec_connec_cost_esc', 'elecCC.elec_connec_cost_esc')
		self.connect('elec_connec_machine_rating_cost_coeff', 'elecCC.elec_connec_machine_rating_cost_coeff')
		self.connect('offshore', 'controlsCC.offshore')
		self.connect('controls_cost_base', 'controlsCC.controls_cost_base')
		self.connect('controls_escalator', 'controlsCC.controls_escalator')
		self.connect('nacelle_platforms_mass_coeff', 'mainframeCC.nacelle_platforms_mass_coeff')
		self.connect('nacelle_platforms_mass_cost_coeff', 'mainframeCC.nacelle_platforms_mass_cost_coeff')
		self.connect('crane', 'mainframeCC.crane')
		self.connect('crane_cost', 'mainframeCC.crane_cost')
		self.connect('bedplate_cost', 'mainframeCC.bedplate_cost')
		self.connect('base_hardware_cost_coeff', 'mainframeCC.base_hardware_cost_coeff')
		self.connect('transformer_mass', 'transformerCC.transformer_mass')
		self.connect('transformer_mass_cost_coeff', 'transformerCC.transformer_mass_cost_coeff')
		
		# connect multipliers
		self.connect('assemblyCostMultiplier', 'ncc.assemblyCostMultiplier')
		self.connect('overheadCostMultiplier' 'ncc.overheadCostMultiplier')
		self.connect('profitMultiplier', 'ncc.profitMultiplier')
		self.connect('transportMultiplier', 'ncc.transportMultiplier')


#==================================================================

def example():

    # test of module for turbine data set

    nacelle = Nacelle_CostsSE()

    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    nacelle.low_speed_shaft_mass = 31257.3
    #nacelle.bearingsMass = 9731.41
    nacelle.main_bearing_mass = 9731.41 / 2.0
    nacelle.second_bearing_mass = 9731.41 / 2.0
    nacelle.gearbox_mass = 30237.60
    nacelle.high_speed_side_mass = 1492.45
    nacelle.generator_mass = 16699.85
    nacelle.bedplate_mass = 93090.6
    nacelle.yaw_system_mass = 11878.24
    nacelle.machine_rating = 5000.0
    nacelle.drivetrain_design = 'geared'
    nacelle.crane = True
    nacelle.offshore = True
    nacelle.year = 2009
    nacelle.month = 12

    nacelle.run()

    print "LSS cost is ${0:.2f} USD".format(nacelle.lssCC.cost) # $183363.52
    print "Main bearings cost is ${0:.2f} USD".format(nacelle.bearingsCC.cost) # $56660.71
    print "Gearbox cost is ${0:.2f} USD".format(nacelle.gearboxCC.cost) # $648030.18
    print "HSS cost is ${0:.2f} USD".format(nacelle.hssCC.cost) # $15218.20
    print "Generator cost is ${0:.2f} USD".format(nacelle.generatorCC.cost) # $435157.75
    print "Bedplate cost is ${0:.2f} USD".format(nacelle.bedplateCC.cost)
    print "Yaw system cost is ${0:.2f} USD".format(nacelle.yawSysCC.cost) # $137609.38

    print "Overall nacelle cost is ${0:.2f} USD".format(nacelle.cost) # $2884227.08
    print

def example_sub():

   # other sub model tests
    print "NREL 5 MW Reference Turbine Component Costs"

    lss = LowSpeedShaftCost()

    lss.low_speed_shaft_mass = 31257.3
    lss.year = 2009
    lss.month = 12
    
    lss.run()
    
    print "LSS cost is ${0:.2f} USD".format(lss.cost)

    bearings = BearingsCost()

    bearings.main_bearing_mass = 9731.41 / 2.0
    bearings.second_bearing_mass = 9731.41 / 2.0
    bearings.year = 2009
    bearings.month = 12

    bearings.run()
    
    print "Main bearings cost is ${0:.2f} USD".format(bearings.cost)

    gearbox = GearboxCost()

    gearbox.gearbox_mass = 30237.60
    gearbox.year = 2009
    gearbox.month = 12
    gearbox.drivetrain_design = 'geared'

    gearbox.run()
    
    print "Gearbox cost is ${0:.2f} USD".format(gearbox.cost)

    hss = HighSpeedSideCost()

    hss.high_speed_side_mass = 1492.45
    hss.year = 2009
    hss.month = 12

    hss.run()

    print "High speed side cost is ${0:.2f} USD".format(hss.cost)

    generator = GeneratorCost()

    generator.generator_mass = 16699.85
    generator.year = 2009
    generator.month = 12
    generator.drivetrain_design = 'geared'
    generator.machine_rating = 5000.0

    generator.run()

    print "Generator cost is ${0:.2f} USD".format(generator.cost)

    bedplate = BedplateCost()

    bedplate.bedplate_mass = 93090.6
    bedplate.year = 2009
    bedplate.month = 12

    bedplate.run()

    print "Bedplate cost is ${0:.2f} USD".format(bedplate.cost)

    yaw = YawSystemCost()

    yaw.yaw_system_mass = 11878.24
    yaw.year = 2009
    yaw.month = 12

    yaw.run()

    print "Yaw system cost is ${0:.2f} USD".format(yaw.cost)

    nacelle = NacelleSystemCostAdder()

    nacelle.bedplate_mass = 93090.6
    nacelle.machine_rating = 5000.0
    nacelle.crane = True
    nacelle.offshore = True
    nacelle.year = 2009
    nacelle.month = 12
    nacelle.lss_cost = 183363.66
    nacelle.bearings_cost = 56660.73
    nacelle.gearbox_cost = 648030.64
    nacelle.hss_cost = 15218.23
    nacelle.generator_cost = 435157.71
    nacelle.bedplate_cost = 138167.19
    nacelle.bedplateCost2002 = 105872.02
    nacelle.yaw_system_cost = 137698.39

    nacelle.run()

    print "Overall nacelle system cost is ${0:.2f} USD".format(nacelle.cost)

if __name__ == '__main__':

    example()

    example_sub()