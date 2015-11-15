"""
turbine_costsse.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int, Enum
import numpy as np

from commonse.config import *

from fusedwind.plant_cost.fused_tcc import FullRotorCostModel, FullRotorCostAggregator, FullHubSystemCostAggregator, BaseComponentCostModel, configure_full_rcc
from fusedwind.plant_cost.fused_tcc import FullNacelleCostModel, BaseComponentCostModel, FullNacelleCostAggregator, configure_full_ncc
from fusedwind.plant_cost.fused_tcc import FullTowerCostModel, FullTowerCostAggregator, BaseComponentCostModel, configure_full_twcc
from fusedwind.plant_cost.fused_tcc import FullTurbineCostModel, FullTCCAggregator, configure_full_tcc
from fusedwind.interface import implement_base


#### Rotor

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BladeCost(Component):

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine blade component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        ppi_labor  = ppi.compute('IPPI_BLL')

        if (self.advanced == True):
            ppi.ref_yr = 2003
            ppi_mat   = ppi.compute('IPPI_BLA')
            slope   = 13.0 #14.0 from model
            intercept     = 5813.9
        else:
            ppi_mat   = ppi.compute('IPPI_BLD')
            slope   = 8.0
            intercept     = 21465.0
        ppi.ref_yr = 2002

        laborCoeff    = 2.7445         # todo: ignoring labor impacts for now
        laborExp      = 2.5025

        self.cost = ((slope*self.blade_mass + intercept)*ppi_mat)

        # derivatives
        self.d_cost_d_blade_mass = slope * ppi_mat

    def list_deriv_vars(self):

        inputs = ['blade_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_blade_mass]])

        return self.J

# -----------------------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HubCost(Component):

    # variables
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine hub component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        hubCost2002      = (self.hub_mass * 4.25) # $/kg
        hubCostEscalator = ppi.compute('IPPI_HUB')
        self.cost = (hubCost2002 * hubCostEscalator )

        # derivatives
        self.d_cost_d_hub_mass = hubCostEscalator * 4.25

    def list_deriv_vars(self):

        inputs = ['hub_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_hub_mass]])

        return self.J



#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class PitchSystemCost(Component):

    # variables
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine pitch system.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        pitchSysCost2002     = 2.28 * (0.0808 * (self.pitch_system_mass ** 1.4985))            # new cost based on mass - x1.328 for housing proportion
        bearingCostEscalator = ppi.compute('IPPI_PMB')
        self.cost = (bearingCostEscalator * pitchSysCost2002)

        # derivatives
        self.d_cost_d_pitch_system_mass = bearingCostEscalator * 2.28 * (0.0808 * 1.4985 * (self.pitch_system_mass ** 0.4985))

    def list_deriv_vars(self):

        inputs = ['pitch_system_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_pitch_system_mass]])

        return self.J


#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class SpinnerCost(Component):

    # variables
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12, iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine spinner component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        #calculate system costs
        ppi_labor  = ppi.compute('IPPI_BLL')

        laborCoeff    = 2.7445
        laborExp      = 2.5025

        spinnerCostEscalator = ppi.compute('IPPI_NAC')
        self.cost = (spinnerCostEscalator * (5.57*self.spinner_mass))

        # derivatives
        self.d_cost_d_spinner_mass = spinnerCostEscalator * 5.57

    def list_deriv_vars(self):

        inputs = ['spinner_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_spinner_mass]])

        return self.J



#-------------------------------------------------------------------------------
@implement_base(FullHubSystemCostAggregator)
class HubSystemCostAdder(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def __init__(self):
        '''
        Computation of overall hub system cost.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.hub_cost + self.pitch_system_cost + self.spinner_cost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_hubCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_pitchSystemCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        self.d_cost_d_spinnerCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

    def list_deriv_vars(self):

        inputs = ['hub_cost', 'pitch_system_cost', 'spinner_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_hubCost, self.d_cost_d_pitchSystemCost, self.d_cost_d_spinnerCost]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostAggregator)
class RotorCostAdder(Component):
    """
    RotorCostAdder adds up individual rotor system and component costs to get overall rotor cost.
    """

    # variables
    blade_cost = Float(iotype='in', units='USD', desc='individual blade cost')
    hub_system_cost = Float(iotype='in', units='USD', desc='cost for hub system')
    
    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def __init__(self):
        '''
        Computation of overall hub system cost.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        self.cost = self.blade_cost * self.blade_number + self.hub_system_cost

        # derivatives
        self.d_cost_d_bladeCost = self.blade_number
        self.d_cost_d_hubSystemCost = 1

    def list_deriv_vars(self):

        inputs = ['blade_cost', 'hub_system_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_bladeCost, self.d_cost_d_hubSystemCost]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostModel)
class Rotor_CostsSE(FullRotorCostModel):

    '''
       Rotor_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters
    year = Int(2010, iotype='in', desc='Current Year')
    month = Int(12,iotype='in', desc='Current Month')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')
    blade_number = Int(iotype='in', desc='number of rotor blades')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def configure(self):

        configure_full_rcc(self)

        # select components
        self.replace('bladeCC', BladeCost())
        self.replace('hubCC', HubCost())
        self.replace('pitchSysCC', PitchSystemCost())
        self.replace('spinnerCC', SpinnerCost())
        self.replace('hubSysCC', HubSystemCostAdder())
        self.replace('rcc', RotorCostAdder())

        # connect inputs
        self.connect('blade_mass', 'bladeCC.blade_mass')
        self.connect('hub_mass', 'hubCC.hub_mass')
        self.connect('pitch_system_mass', 'pitchSysCC.pitch_system_mass')
        self.connect('spinner_mass', 'spinnerCC.spinner_mass')
        self.connect('year', ['hubCC.year', 'pitchSysCC.year', 'spinnerCC.year', 'bladeCC.year'])
        self.connect('month', ['hubCC.month', 'pitchSysCC.month', 'spinnerCC.month', 'bladeCC.month'])
        self.connect('advanced', 'bladeCC.advanced')
    

def example_rotor():

    # simple test of module
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    # NREL 5 MW turbine
    print "NREL 5 MW turbine test"
    rotor = Rotor_CostsSE()

    # Blade Test 1
    rotor.blade_number = 3
    rotor.advanced = True
    rotor.blade_mass = 17650.67  # inline with the windpact estimates
    rotor.hub_mass = 31644.5
    rotor.pitch_system_mass = 17004.0
    rotor.spinner_mass = 1810.5
    rotor.year = 2009
    rotor.month = 12

    rotor.run()

    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(rotor.cost)
    print

def example_rotor_subs():

   # other sub model tests

    print "NREL 5 MW Reference Turbine Component Costs"

    blade = BladeCost()

    blade.blade_mass = 17650.67
    blade.year = 2009
    blade.month = 12
    
    blade.run()
    
    print "Blade cost is ${0:.2f} USD".format(blade.cost)

    hub = HubCost()

    hub.hub_mass = 31644.5
    hub.year = 2009
    hub.month = 12
    
    hub.run()
    
    print "Hub cost is ${0:.2f} USD".format(hub.cost)

    pitch = PitchSystemCost()

    pitch.pitch_system_mass = 17004.0
    pitch.year = 2009
    pitch.month = 12

    pitch.run()

    print "Hub cost is ${0:.2f} USD".format(pitch.cost)

    spinner = SpinnerCost()

    spinner.spinner_mass = 1810.5
    spinner.year = 2009
    spinner.month = 12

    spinner.run()

    print "Spinner cost is ${0:.2f} USD".format(spinner.cost)


##### Nacelle

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




#==================================================================

def example_nacelle():

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

def example_nacelle_subs():

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


##### Tower

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class TowerCost(Component):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine tower component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        twrCostEscalator  = ppi.compute('IPPI_TWR')

        twrCostCoeff      = 1.5 # $/kg

        self.towerCost2002 = self.tower_mass * twrCostCoeff
        self.cost = self.towerCost2002 * twrCostEscalator

        # derivatives
        self.d_cost_d_tower_mass = twrCostEscalator * twrCostCoeff

    def list_deriv_vars(self):

        inputs = ['tower_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_tower_mass]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullTowerCostAggregator)
class TowerCostAdder(Component):

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost') 

    def __init__(self):

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.tower_cost
        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_tower_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

    def list_deriv_vars(self):

        inputs = ['tower_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_tower_cost]])

        return self.J

#-------------------------------------------------------------------------------
@implement_base(FullTowerCostModel)
class Tower_CostsSE(Assembly):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def configure(self):

        configure_full_twcc(self)

        self.replace('towerCC', TowerCost())
        self.replace('twrcc', TowerCostAdder())

        self.connect('tower_mass', 'towerCC.tower_mass')
        self.connect('year', 'towerCC.year')
        self.connect('month', 'towerCC.month')


#-------------------------------------------------------------------------------

def example_tower():

    # simple test of module
    tower = Tower_CostsSE()

    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    tower.tower_mass = 434559.0
    tower.year = 2009
    tower.month =  12

    tower.run()

    print "Tower cost is ${0:.2f} USD".format(tower.cost) # $987180.30


##### Turbine

#-------------------------------------------------------------------------------
@implement_base(FullTurbineCostModel)
class Turbine_CostsSE(Assembly):

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    second_bearing_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass')
    generator_mass = Float(iotype='in', units='kg', desc='component mass')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass')
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
    advanced_blade = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design')
    drivetrain_design = Enum('geared', ('geared', 'single_stage', 'multi_drive', 'pm_direct_drive'), iotype='in')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore site')
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def configure(self):

        configure_full_tcc(self)

        # select components
        self.replace('rotorCC', Rotor_CostsSE())
        self.replace('nacelleCC', Nacelle_CostsSE())
        self.replace('towerCC', Tower_CostsSE())
        self.replace('tcc', TurbineCostAdder())

        # connect inputs
        self.connect('blade_mass', 'rotorCC.blade_mass')
        self.connect('blade_number', 'rotorCC.blade_number')
        self.connect('hub_mass', 'rotorCC.hub_mass')
        self.connect('pitch_system_mass', 'rotorCC.pitch_system_mass')
        self.connect('spinner_mass', 'rotorCC.spinner_mass')
        self.connect('advanced_blade', 'rotorCC.advanced')
        self.connect('low_speed_shaft_mass', 'nacelleCC.low_speed_shaft_mass')
        self.connect('main_bearing_mass', 'nacelleCC.main_bearing_mass')
        self.connect('second_bearing_mass', 'nacelleCC.second_bearing_mass')
        self.connect('gearbox_mass', 'nacelleCC.gearbox_mass')
        self.connect('high_speed_side_mass', 'nacelleCC.high_speed_side_mass')
        self.connect('generator_mass', 'nacelleCC.generator_mass')
        self.connect('bedplate_mass', ['nacelleCC.bedplate_mass'])
        self.connect('yaw_system_mass', 'nacelleCC.yaw_system_mass')
        self.connect('machine_rating', ['nacelleCC.machine_rating'])
        self.connect('drivetrain_design', ['nacelleCC.drivetrain_design'])
        self.connect('crane', 'nacelleCC.crane')
        self.connect('offshore', ['nacelleCC.offshore', 'tcc.offshore'])
        self.connect('tower_mass', 'towerCC.tower_mass')
        self.connect('year', ['rotorCC.year', 'nacelleCC.year', 'towerCC.year'])
        self.connect('month', ['rotorCC.month', 'nacelleCC.month', 'towerCC.month'])
        
        self.create_passthrough('tcc.assemblyCostMultiplier')
        self.create_passthrough('tcc.overheadCostMultiplier')
        self.create_passthrough('tcc.profitMultiplier')
        self.create_passthrough('tcc.transportMultiplier')


#-------------------------------------------------------------------------------
@implement_base(FullTCCAggregator)
class TurbineCostAdder(Component):

    # Variables
    rotor_cost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelle_cost = Float(iotype='in', units='USD', desc='nacelle cost')
    tower_cost = Float(iotype='in', units='USD', desc='tower cost')

    # parameters
    offshore = Bool(iotype='in', desc='flag for offshore site')
    assemblyCostMultiplier = Float(0.0, iotype='in', desc='multiplier for assembly cost in manufacturing')
    overheadCostMultiplier = Float(0.0, iotype='in', desc='multiplier for overhead')
    profitMultiplier = Float(0.0, iotype='in', desc='multiplier for profit markup')
    transportMultiplier = Float(0.0, iotype='in', desc='multiplier for transport costs')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')

    def __init__(self):

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        self.turbine_cost = (1 + self.transportMultiplier + self.profitMultiplier) * ((1+self.overheadCostMultiplier+self.assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_rotor_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)
        self.d_cost_d_nacelle_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)
        self.d_cost_d_tower_cost = (1 + self.transportMultiplier + self.profitMultiplier) * (1+self.overheadCostMultiplier+self.assemblyCostMultiplier)

        if self.offshore:
            self.turbine_cost *= 1.1

            # derivatives
            self.d_cost_d_rotor_cost *= 1.1
            self.d_cost_d_nacelle_cost *= 1.1
            self.d_cost_d_tower_cost *= 1.1

    def list_deriv_vars(self):

        inputs = ['rotor_cost', 'nacelle_cost', 'tower_cost']
        outputs = ['turbine_cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_rotor_cost, self.d_cost_d_nacelle_cost, self.d_cost_d_tower_cost]])

        return self.J

#-------------------------------------------------------------------------------

def example_turbine():

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
    print "LSS cost is ${0:.2f} USD".format(turbine.nacelleCC.lssCC.cost)
    print "Main bearings cost is ${0:.2f} USD".format(turbine.nacelleCC.bearingsCC.cost)
    print "Gearbox cost is ${0:.2f} USD".format(turbine.nacelleCC.gearboxCC.cost)
    print "High speed side cost is ${0:.2f} USD".format(turbine.nacelleCC.hssCC.cost)
    print "Generator cost is ${0:.2f} USD".format(turbine.nacelleCC.generatorCC.cost)
    print "Bedplate cost is ${0:.2f} USD".format(turbine.nacelleCC.bedplateCC.cost)
    print "Yaw system cost is ${0:.2f} USD".format(turbine.nacelleCC.yawSysCC.cost)
    print
    print "Tower cost is ${0:.2f} USD".format(turbine.towerCC.cost)
    print
    print "The overall turbine cost is ${0:.2f} USD".format(turbine.turbine_cost)
    print

if __name__ == "__main__":

    example_turbine()
    
    #example_rotor()
    
    #example_rotor_subs()
    
    #example_nacelle()
    
    #example_nacelle_subs()
    
    #example_tower()
    