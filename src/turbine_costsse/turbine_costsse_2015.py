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
from fusedwind.plant_cost.fused_tcc import FullRotorCostModel, FullRotorCostAggregator, FullHubSystemCostAggregator, BaseComponentCostModel, configure_full_rcc
from fusedwind.plant_cost.fused_tcc import FullNacelleCostModel, BaseComponentCostModel, FullNacelleCostAggregator, configure_full_ncc
from fusedwind.plant_cost.fused_tcc import FullTowerCostModel, FullTowerCostAggregator, BaseComponentCostModel, configure_full_twcc


###### Rotor

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BladeCost2015(Component):

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    blade_mass_cost_coeff = Float(13.92, iotype='in', units='USD/kg', desc='blade mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capital costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        BladeCost2015 = self.blade_mass_cost_coeff * self.blade_mass
        self.cost = BladeCost2015
        

# -----------------------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HubCost2015(Component):

    # variables
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass_cost_coeff = Float(3.80, iotype='in', units='USD/kg', desc='hub mass-cost coefficient [$/kg]')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        HubCost2015 = self.hub_mass_cost_coeff * self.hub_mass
        self.cost = HubCost2015
        

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class PitchSystemCost2015(Component):

    # variables
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass_cost_coeff = Float(22.91, iotype='in', units='USD/kg', desc='pitch system mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        #calculate system costs
        PitchSystemCost2015 = self.pitch_system_mass_cost_coeff * self.pitch_system_mass
        self.cost = PitchSystemCost2015
        
#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class SpinnerCost2015(Component):

    # variables
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass_cost_coeff = Float(15.59, iotype='in', units='USD/kg', desc='spinner/nose cone mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        #calculate system costs
        SpinnerCost2015 = self.spinner_mass_cost_coeff * self.spinner_mass
        self.cost = SpinnerCost2015

#-------------------------------------------------------------------------------
@implement_base(FullHubSystemCostAggregator)
class HubSystemCostAdder2015(Component):

    # variables
    hub_cost = Float(iotype='in', units='USD', desc='hub component cost')
    pitch_system_cost = Float(iotype='in', units='USD', desc='pitch system cost')
    spinner_cost = Float(iotype='in', units='USD', desc='spinner component cost')
    
    # multipliers
    hub_assemblyCostMultiplier = Float(0.0, iotype='in', desc='rotor assembly cost multiplier')
    hub_overheadCostMultiplier = Float(0.0, iotype='in', desc='rotor overhead cost multiplier')
    hub_profitMultiplier = Float(0.0, iotype='in', desc='rotor profit multiplier')
    hub_transportMultiplier = Float(0.0, iotype='in', desc='rotor transport multiplier')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def execute(self):

        partsCost = self.hub_cost + self.pitch_system_cost + self.spinner_cost
        
        # updated calculations below to account for assembly, transport, overhead and profit
        self.cost = (1 + self.hub_transportMultiplier + self.hub_profitMultiplier) * ((1 + self.hub_overheadCostMultiplier + self.hub_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostAggregator)
class RotorCostAdder2015(Component):
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

    def execute(self):

        self.cost = self.blade_cost * self.blade_number + self.hub_system_cost

#-------------------------------------------------------------------------------
@implement_base(FullRotorCostModel)
class Rotor_CostsSE_2015(FullRotorCostModel):

    '''
       Rotor_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    blade_mass_cost_coeff = Float(13.08, iotype='in', units='USD/kg', desc='blade mass-cost coefficient [$/kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass_cost_coeff = Float(3.80, iotype='in', units='USD/kg', desc='hub mass-cost coefficient [$/kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass_cost_coeff = Float(22.91, iotype='in', units='USD/kg', desc='pitch system mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass_cost_coeff = Float(15.59, iotype='in', units='USD/kg', desc='spinner/nose cone mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # parameters
    blade_number = Int(iotype='in', desc='number of rotor blades')
  
    #multipliers
    hub_assemblyCostMultiplier = Float(0.0, iotype='in', desc='rotor assembly cost multiplier')
    hub_overheadCostMultiplier = Float(0.0, iotype='in', desc='rotor overhead cost multiplier')
    hub_profitMultiplier = Float(0.0, iotype='in', desc='rotor profit multiplier')
    hub_transportMultiplier = Float(0.0, iotype='in', desc='rotor transport multiplier')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind sub-assembly capial costs including transportation costs')

    def configure(self):

        configure_full_rcc(self)

        # select components
        self.replace('bladeCC', BladeCost2015())
        self.replace('hubCC', HubCost2015())
        self.replace('pitchSysCC', PitchSystemCost2015())
        self.replace('spinnerCC', SpinnerCost2015())
        self.replace('hubSysCC', HubSystemCostAdder2015())
        self.replace('rcc', RotorCostAdder2015())

        # connect inputs
        self.connect('blade_mass', 'bladeCC.blade_mass')
        self.connect('blade_mass_cost_coeff', 'bladeCC.blade_mass_cost_coeff')
        self.connect('hub_mass', 'hubCC.hub_mass')
        self.connect('hub_mass_cost_coeff', 'hubCC.hub_mass_cost_coeff')
        self.connect('pitch_system_mass', 'pitchSysCC.pitch_system_mass')
        self.connect('pitch_system_mass_cost_coeff', 'pitchSysCC.pitch_system_mass_cost_coeff')
        self.connect('spinner_mass', 'spinnerCC.spinner_mass')
        self.connect('spinner_mass_cost_coeff', 'spinnerCC.spinner_mass_cost_coeff')
    
        # connect multipliers
        self.connect('hub_assemblyCostMultiplier', 'hubSysCC.hub_assemblyCostMultiplier')
        self.connect('hub_overheadCostMultiplier', 'hubSysCC.hub_overheadCostMultiplier')
        self.connect('hub_profitMultiplier', 'hubSysCC.hub_profitMultiplier')
        self.connect('hub_transportMultiplier', 'hubSysCC.hub_transportMultiplier')

#-------------------------------------------------------------------------------


###### Nacelle

# -------------------------------------------------
@implement_base(BaseComponentCostModel)
class LowSpeedShaftCost2015(Component):

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
    lss_mass_cost_coeff = Float(13.30, iotype='in', units='USD/kg', desc='low speed shaft mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs') #initialize cost output

    def execute(self):

        # calculate component cost
        LowSpeedShaftCost2015 = self.lss_mass_cost_coeff * self.low_speed_shaft_mass
        self.cost = LowSpeedShaftCost2015 #assign the cost to this object so don't have to return anything

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BearingsCost2015(Component):

    # variables
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
    bearing_number = Float(2, iotype='in', desc='number of main bearings []') #number of main bearings- defaults to 2
    bearings_mass_cost_coeff = Float(6.35, iotype='in', units='USD/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):
    
        #calculate component cost
        BearingsCost2015 = self.bearings_mass_cost_coeff * self.main_bearing_mass * self.bearing_number
        self.cost = BearingsCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GearboxCost2015(Component):

    # variables
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    gearbox_mass_cost_coeff = Float(18.14, iotype='in', units='USD/kg', desc='gearbox mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        GearboxCost2015 = self.gearbox_mass_cost_coeff * self.gearbox_mass
        self.cost = GearboxCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HighSpeedSideCost2015(Component):

    # variables
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    high_speed_side_mass_cost_coeff = Float(9.55, iotype='in', units='USD/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        MechBrakeCost2015 = self.high_speed_side_mass_cost_coeff * self.high_speed_side_mass
        self.cost = MechBrakeCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class GeneratorCost2015(Component):

    # variables
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    generator_mass_cost_coeff = Float(17.46, iotype='in', units= 'USD/kg', desc='generator mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        #calculate component cost
        GeneratorCost2015 = self.generator_mass_cost_coeff * self.generator_mass
        self.cost = GeneratorCost2015

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class BedplateCost2015(Component):

    # variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    bedplate_mass_cost_coeff = Float(4.00, iotype='in', units='USD/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        BedplateCost2015 = self.bedplate_mass_cost_coeff * self.bedplate_mass
        self.cost = BedplateCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class YawSystemCost2015(Component):

    # variables
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    yaw_system_mass_cost_coeff = Float(11.74, iotype='in', units='USD/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate cost
        YawSystemCost2015 = self.yaw_system_mass_cost_coeff * self.yaw_system_mass
        self.cost = YawSystemCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class VariableSpeedElecCost2015(Component):

    # variables
    variable_speed_elec_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='USD/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate cost
        VariableSpeedElecCost2015 = self.variable_speed_elec_mass_cost_coeff * self.variable_speed_elec_mass
        self.cost = VariableSpeedElecCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class HydraulicCoolingCost2015(Component):

    # variables
    hydraulic_cooling_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hydraulic_cooling_mass_cost_coeff = Float(174.63, iotype='in', units='USD/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate cost
        HydraulicCoolingCost2015 = self.hydraulic_cooling_mass_cost_coeff * self.hydraulic_cooling_mass
        self.cost = HydraulicCoolingCost2015

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class NacelleCoverCost2015(Component):

    # variables
    nacelle_cover_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_cover_mass_cost_coeff = Float(8.07, iotype='in', units='USD/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

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
    elec_connec_machine_rating_cost_coeff = Float(40.0, iotype='in', units='USD/kW', desc='2002 electrical connections cost coefficient per kW') #default from old CSM

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

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

    def execute(self):

        if (not self.offshore):
            ControlsCost = self.controls_cost_base[0] * self.controls_escalator
        else:
            ControlsCost  = self.controls_cost_base[1] * self.controls_escalator
        self.cost = ControlsCost

#---------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class OtherMainframeCost2015(Component):

    #model all three (nacelle platform, service crane, and base hardware) from old model
  
    # variables
    nacelle_platforms_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_platforms_mass_cost_coeff = Float(8.7, iotype='in', units='USD/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    bedplate_cost = Float(iotype='in', units='USD', desc='component cost [USD]')
    base_hardware_cost_coeff = Float(0.7, iotype='in', desc='base hardware cost coefficient based on bedplate cost') #default from old CSM

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # nacelle platform cost
        NacellePlatformsCost = self.nacelle_platforms_mass_cost_coeff * self.nacelle_platforms_mass

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
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= 'USD/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        #calculate component cost
        TransformerCost2015 = self.transformer_mass_cost_coeff * self.transformer_mass
        self.cost = TransformerCost2015

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
    nacelle_assemblyCostMultiplier = Float(0.0, iotype='in', desc='nacelle assembly cost multiplier')
    nacelle_overheadCostMultiplier = Float(0.0, iotype='in', desc='nacelle overhead cost multiplier')
    nacelle_profitMultiplier = Float(0.0, iotype='in', desc='nacelle profit multiplier')
    nacelle_transportMultiplier = Float(0.0, iotype='in', desc='nacelle transport multiplier')

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

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
        self.cost = (1 + self.nacelle_transportMultiplier + self.nacelle_profitMultiplier) * ((1 + self.nacelle_overheadCostMultiplier + self.nacelle_assemblyCostMultiplier) * partsCost)

#---------------------------------------------------------------------------------------------
class Nacelle_CostsSE_2015(FullNacelleCostModel):

    '''
       Nacelle_CostsSE class
          The Rotor_costsSE class is used to represent the rotor costs of a wind turbine.
    '''

    # variables
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    variable_speed_elec_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hydraulic_cooling_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_cover_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_platforms_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    transformer_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters / high level inputs
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    offshore = Bool(iotype='in', desc='flag for offshore project')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    bearing_number = Float(2, iotype='in', desc='number of main bearings []') #number of main bearings- defaults to 2

    # coefficients
    lss_mass_cost_coeff = Float(13.30, iotype='in', units='USD/kg', desc='low speed shaft mass-cost coefficient [$/kg]')
    bearings_mass_cost_coeff = Float(6.35, iotype='in', units='USD/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings 
    gearbox_mass_cost_coeff = Float(18.46, iotype='in', units='USD/kg', desc='gearbox mass-cost coefficient [$/kg]')
    high_speed_side_mass_cost_coeff = Float(9.55, iotype='in', units='USD/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    generator_mass_cost_coeff = Float(17.46, iotype='in', units= 'USD/kg', desc='generator mass cost coefficient [$/kg]')
    bedplate_mass_cost_coeff = Float(4.00, iotype='in', units='USD/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    yaw_system_mass_cost_coeff = Float(11.74, iotype='in', units='USD/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='USD/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    hydraulic_cooling_mass_cost_coeff = Float(174.62, iotype='in', units='USD/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    nacelle_cover_mass_cost_coeff = Float(8.07, iotype='in', units='USD/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    elec_connec_cost_esc = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for electrical connections') ####KLD update this
    elec_connec_machine_rating_cost_coeff = Float(40.0, iotype='in', units='USD/kW', desc='2002 electrical connections cost coefficient per kW')
    controls_cost_base = Array(np.array([35000.0,55900.0]), iotype='in', desc='2002 controls cost for [onshore, offshore]')
    controls_escalator = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for controls') ####KLD update this
    nacelle_platforms_mass_cost_coeff = Float(8.07, iotype='in', units='USD/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    base_hardware_cost_coeff = Float(0.7, iotype='in', desc='base hardware cost coefficient based on bedplate cost') #default from old CSM
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= 'USD/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

  
    #multipliers
    nacelle_assemblyCostMultiplier = Float(0.0, iotype='in', desc='nacelle assembly cost multiplier')
    nacelle_overheadCostMultiplier = Float(0.0, iotype='in', desc='nacelle overhead cost multiplier')
    nacelle_profitMultiplier = Float(0.0, iotype='in', desc='nacelle profit multiplier')
    nacelle_transportMultiplier = Float(0.0, iotype='in', desc='nacelle transport multiplier')

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
        self.add('vsCC', VariableSpeedElecCost2015())
        self.add('hydraulicCC', HydraulicCoolingCost2015())
        self.add('nacelleCC', NacelleCoverCost2015())
        self.add('elecCC', ElecConnecCost2015())
        self.add('controlsCC', ControlsCost2015())
        self.add('mainframeCC', OtherMainframeCost2015())
        self.add('transformerCC', TransformerCost2015())
        self.replace('ncc', NacelleSystemCostAdder2015())
        
        self.driver.workflow.add(['vsCC', 'hydraulicCC', 'nacelleCC', 'elecCC', 'controlsCC', 'mainframeCC', 'transformerCC'])

        # connect inputs
        self.connect('low_speed_shaft_mass', 'lssCC.low_speed_shaft_mass')
        self.connect('lss_mass_cost_coeff', 'lssCC.lss_mass_cost_coeff')
        self.connect('main_bearing_mass', 'bearingsCC.main_bearing_mass')
        self.connect('bearing_number', 'bearingsCC.bearing_number')
        self.connect('bearings_mass_cost_coeff', 'bearingsCC.bearings_mass_cost_coeff')
        self.connect('gearbox_mass', 'gearboxCC.gearbox_mass')
        self.connect('gearbox_mass_cost_coeff', 'gearboxCC.gearbox_mass_cost_coeff')
        self.connect('high_speed_side_mass', 'hssCC.high_speed_side_mass')
        self.connect('high_speed_side_mass_cost_coeff', 'hssCC.high_speed_side_mass_cost_coeff')
        self.connect('generator_mass', 'generatorCC.generator_mass')
        self.connect('generator_mass_cost_coeff', 'generatorCC.generator_mass_cost_coeff')
        self.connect('bedplate_mass', ['bedplateCC.bedplate_mass'])
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
        self.connect('nacelle_platforms_mass', 'mainframeCC.nacelle_platforms_mass')
        self.connect('nacelle_platforms_mass_cost_coeff', 'mainframeCC.nacelle_platforms_mass_cost_coeff')
        self.connect('crane', 'mainframeCC.crane')
        self.connect('crane_cost', 'mainframeCC.crane_cost')
        self.connect('base_hardware_cost_coeff', 'mainframeCC.base_hardware_cost_coeff')
        self.connect('transformer_mass', 'transformerCC.transformer_mass')
        self.connect('transformer_mass_cost_coeff', 'transformerCC.transformer_mass_cost_coeff')

        # internal connections
        self.connect('bedplateCC.cost', 'mainframeCC.bedplate_cost')
        
        # connect multipliers
        self.connect('nacelle_assemblyCostMultiplier', 'ncc.nacelle_assemblyCostMultiplier')
        self.connect('nacelle_overheadCostMultiplier', 'ncc.nacelle_overheadCostMultiplier')
        self.connect('nacelle_profitMultiplier', 'ncc.nacelle_profitMultiplier')
        self.connect('nacelle_transportMultiplier', 'ncc.nacelle_transportMultiplier')


###### Tower

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class TowerCost2015(Component):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    tower_mass_cost_coefficient = Float(3.08, iotype='in', units='USD/kg', desc='tower mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def execute(self):

        # calculate component cost
        TowerCost2015 = self.tower_mass_cost_coefficient * self.tower_mass
        self.cost = TowerCost2015

#-------------------------------------------------------------------------------
@implement_base(FullTowerCostAggregator)
class TowerCostAdder2015(Component):

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
  
    # multipliers
    tower_assemblyCostMultiplier = Float(0.0, iotype='in', desc='tower assembly cost multiplier')
    tower_overheadCostMultiplier = Float(0.0, iotype='in', desc='tower overhead cost multiplier')
    tower_profitMultiplier = Float(0.0, iotype='in', desc='tower profit cost multiplier')
    tower_transportMultiplier = Float(0.0, iotype='in', desc='tower transport cost multiplier')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost') 

    def execute(self):

        partsCost = self.tower_cost
        self.cost = (1 + self.tower_transportMultiplier + self.tower_profitMultiplier) * ((1 + self.tower_overheadCostMultiplier + self.tower_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------
@implement_base(FullTowerCostModel)
class Tower_CostsSE_2015(Assembly):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    tower_mass_cost_coefficient = Float(3.08, iotype='in', units='USD/kg', desc='tower mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    
    # multipliers
    tower_assemblyCostMultiplier = Float(0.0, iotype='in', desc='tower assembly cost multiplier')
    tower_overheadCostMultiplier = Float(0.0, iotype='in', desc='tower overhead cost multiplier')
    tower_profitMultiplier = Float(0.0, iotype='in', desc='tower profit cost multiplier')
    tower_transportMultiplier = Float(0.0, iotype='in', desc='tower transport cost multiplier')

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def configure(self):

        configure_full_twcc(self)

        # create instances of components
        self.replace('towerCC', TowerCost2015())
        self.replace('twrcc', TowerCostAdder2015())
    
        # connect inputs
        self.connect('tower_mass', 'towerCC.tower_mass')
        self.connect('tower_mass_cost_coefficient', 'towerCC.tower_mass_cost_coefficient')
        
        # connect multipliers
        self.connect('tower_assemblyCostMultiplier', 'twrcc.tower_assemblyCostMultiplier')
        self.connect('tower_overheadCostMultiplier', 'twrcc.tower_overheadCostMultiplier')
        self.connect('tower_profitMultiplier', 'twrcc.tower_profitMultiplier')
        self.connect('tower_transportMultiplier', 'twrcc.tower_transportMultiplier')



#-------------------------------------------------------------------------------
@implement_base(FullTurbineCostModel)
class Turbine_CostsSE_2015(Assembly):

    # variables
    blade_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hub_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitch_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinner_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    low_speed_shaft_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    main_bearing_mass = Float(iotype='in', units='kg', desc='component mass [kg]') #mass input
    gearbox_mass = Float(iotype='in', units='kg', desc='component mass')
    high_speed_side_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    generator_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    yaw_system_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    variable_speed_elec_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hydraulic_cooling_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_cover_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_platforms_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    transformer_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    tower_mass = Float(iotype='in', units='kg', desc='component mass [kg]')

    # parameters / high level inputs
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    blade_number = Int(iotype='in', desc='number of rotor blades')
    offshore = Bool(iotype='in', desc='flag for offshore project')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    bearing_number = Float(2, iotype='in', desc='number of main bearings []') #number of main bearings- defaults to 2

    # cost coefficients
    blade_mass_cost_coeff = Float(13.93, iotype='in', units='USD/kg', desc='blade mass-cost coefficient [$/kg]')
    hub_mass_cost_coeff = Float(3.80, iotype='in', units='USD/kg', desc='hub mass-cost coefficient [$/kg]')
    pitch_system_mass_cost_coeff = Float(22.91, iotype='in', units='USD/kg', desc='pitch system mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    spinner_mass_cost_coeff = Float(15.60, iotype='in', units='USD/kg', desc='spinner/nose cone mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    lss_mass_cost_coeff = Float(13.30, iotype='in', units='USD/kg', desc='low speed shaft mass-cost coefficient [$/kg]')
    bearings_mass_cost_coeff = Float(6.35, iotype='in', units='USD/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings 
    gearbox_mass_cost_coeff = Float(18.46, iotype='in', units='USD/kg', desc='gearbox mass-cost coefficient [$/kg]')
    high_speed_side_mass_cost_coeff = Float(9.55, iotype='in', units='USD/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    generator_mass_cost_coeff = Float(17.46, iotype='in', units= 'USD/kg', desc='generator mass cost coefficient [$/kg]')
    bedplate_mass_cost_coeff = Float(4.00, iotype='in', units='USD/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    yaw_system_mass_cost_coeff = Float(11.74, iotype='in', units='USD/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='USD/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    hydraulic_cooling_mass_cost_coeff = Float(174.62, iotype='in', units='USD/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    nacelle_cover_mass_cost_coeff = Float(8.07, iotype='in', units='USD/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    elec_connec_cost_esc = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for electrical connections') ####KLD update this
    elec_connec_machine_rating_cost_coeff = Float(40.0, iotype='in', units='USD/kW', desc='2002 electrical connections cost coefficient per kW')
    controls_cost_base = Array(np.array([35000.0,55900.0]), iotype='in', desc='2002 controls cost for [onshore, offshore]')
    controls_escalator = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for controls') ####KLD update this
    nacelle_platforms_mass_cost_coeff = Float(8.07, iotype='in', units='USD/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    base_hardware_cost_coeff = Float(0.7, iotype='in', desc='base hardware cost coefficient based on bedplate cost') #default from old CSM
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= 'USD/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    tower_mass_cost_coefficient = Float(3.08, iotype='in', units='USD/kg', desc='tower mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
  
    #multipliers
    hub_assemblyCostMultiplier = Float(0.0, iotype='in', desc='rotor assembly cost multiplier')
    hub_overheadCostMultiplier = Float(0.0, iotype='in', desc='rotor overhead cost multiplier')
    hub_profitMultiplier = Float(0.0, iotype='in', desc='rotor profit multiplier')
    hub_transportMultiplier = Float(0.0, iotype='in', desc='rotor transport multiplier')

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
        self.connect('bearing_number', 'nacelleCC.bearing_number')
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
        self.connect('base_hardware_cost_coeff', 'nacelleCC.base_hardware_cost_coeff')
        self.connect('transformer_mass', 'nacelleCC.transformer_mass')
        self.connect('transformer_mass_cost_coeff', 'nacelleCC.transformer_mass_cost_coeff')
        self.connect('tower_mass', 'towerCC.tower_mass')
        
        # connect multipliers
        self.connect('hub_assemblyCostMultiplier', 'rotorCC.hub_assemblyCostMultiplier')
        self.connect('hub_overheadCostMultiplier', 'rotorCC.hub_overheadCostMultiplier')
        self.connect('hub_profitMultiplier', 'rotorCC.hub_profitMultiplier')
        self.connect('hub_transportMultiplier', 'rotorCC.hub_transportMultiplier')
        self.connect('nacelle_assemblyCostMultiplier', 'nacelleCC.nacelle_assemblyCostMultiplier')
        self.connect('nacelle_overheadCostMultiplier', 'nacelleCC.nacelle_overheadCostMultiplier')
        self.connect('nacelle_profitMultiplier', 'nacelleCC.nacelle_profitMultiplier')
        self.connect('nacelle_transportMultiplier', 'nacelleCC.nacelle_transportMultiplier')
        self.connect('tower_assemblyCostMultiplier', 'towerCC.tower_assemblyCostMultiplier')
        self.connect('tower_overheadCostMultiplier', 'towerCC.tower_overheadCostMultiplier')
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

    def execute(self):

        partsCost = self.rotor_cost + self.nacelle_cost + self.tower_cost

        self.turbine_cost = (1 + self.turbine_transportMultiplier + self.turbine_profitMultiplier) * ((1 + self.turbine_overheadCostMultiplier + self.turbine_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------

def example():

    # simple test of module

    turbine = Turbine_CostsSE_2015()

    turbine.blade_mass = 17650.67  # inline with the windpact estimates
    turbine.hub_mass = 31644.5
    turbine.pitch_system_mass = 17004.0
    turbine.spinner_mass = 1810.5
    turbine.low_speed_shaft_mass = 31257.3
    #bearingsMass = 9731.41
    turbine.main_bearing_mass = 9731.41 / 2
    turbine.second_bearing_mass = 9731.41 / 2 #KLD - revisit this in new model
    turbine.gearbox_mass = 30237.60
    turbine.high_speed_side_mass = 1492.45
    turbine.generator_mass = 16699.85
    turbine.bedplate_mass = 93090.6
    turbine.yaw_system_mass = 11878.24
    turbine.tower_mass = 434559.0
    turbine.variable_speed_elec_mass = 1000. #Float(iotype='in', units='kg', desc='component mass [kg]')
    turbine.hydraulic_cooling_mass = 1000. #Float(iotype='in', units='kg', desc='component mass [kg]')
    turbine.nacelle_cover_mass = 1000. #Float(iotype='in', units='kg', desc='component mass [kg]')
    turbine.nacelle_platforms_mass = 1000. #Float(iotype='in', units='kg', desc='component mass [kg]')
    turbine.transformer_mass = 1000. #Float(iotype='in', units='kg', desc='component mass [kg]')    

    # other inputs
    turbine.machine_rating = 5000.0
    turbine.blade_number = 3
    turbine.crane = True
    turbine.offshore = True
    turbine.bearing_number = 2

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
    print "Variable speed electronics cost is ${0:.2f} USD".format(turbine.nacelleCC.vsCC.cost)
    print "HVAC cost is ${0:.2f} USD".format(turbine.nacelleCC.hydraulicCC.cost)    
    print "Electrical connections cost is ${0:.2f} USD".format(turbine.nacelleCC.elecCC.cost)
    print "Controls cost is ${0:.2f} USD".format(turbine.nacelleCC.controlsCC.cost)
    print "Mainframe cost is ${0:.2f} USD".format(turbine.nacelleCC.mainframeCC.cost)
    print "Transformer cost is ${0:.2f} USD".format(turbine.nacelleCC.transformerCC.cost)
    print
    print "Tower cost is ${0:.2f} USD".format(turbine.towerCC.cost)
    print
    print "The overall turbine cost is ${0:.2f} USD".format(turbine.turbine_cost)
    print


if __name__ == "__main__":

    example()