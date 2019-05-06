"""
turbine_costsse_2015.py

Created by Janine Freeman 2015 based on turbine_costsse.py 2012.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.api import Component, Problem, Group, IndepVarComp

import numpy as np

###### Rotor
#-------------------------------------------------------------------------------
class BladeCost2015(Component):

    def __init__(self):

        super(BladeCost2015, self).__init__()

        # Inputs
        self.add_param('blade_mass',            0.0,  units='kg',     desc='component mass')
        self.add_param('blade_mass_cost_coeff', 14.6, units='USD/kg', desc='blade mass-cost coeff')
        self.add_param('blade_cost_external',   0.0,  units='USD',    desc='Blade cost computed by RotorSE')
        
        # Outputs
        self.add_output('blade_cost',           0.0,  units='USD',    desc='Overall wind turbine component capital costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        blade_mass = params['blade_mass']
        blade_mass_cost_coeff = params['blade_mass_cost_coeff']

        # calculate component cost
        if params['blade_cost_external'] < 1.:
            unknowns['blade_cost'] = blade_mass_cost_coeff * blade_mass
        else:
            unknowns['blade_cost'] = params['blade_cost_external']
        

# -----------------------------------------------------------------------------------------------
class HubCost2015(Component):

    def __init__(self):

        super(HubCost2015, self).__init__()

        # variables
        self.add_param('hub_mass', 0.0, desc='component mass', units='kg')
        self.add_param('hub_mass_cost_coeff', 3.9, desc='hub mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('hub_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        hub_mass_cost_coeff = params['hub_mass_cost_coeff']
        hub_mass = params['hub_mass']

        # calculate component cost
        HubCost2015 = hub_mass_cost_coeff * hub_mass
        unknowns['hub_cost'] = HubCost2015
        

#-------------------------------------------------------------------------------
class PitchSystemCost2015(Component):

    def __init__(self):

        super(PitchSystemCost2015,self).__init__()

        # variables
        self.add_param('pitch_system_mass', 0.0, desc='component mass', units='kg')
        self.add_param('pitch_system_mass_cost_coeff', 22.1, desc='pitch system mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('pitch_system_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):
        
        pitch_system_mass = params['pitch_system_mass']
        pitch_system_mass_cost_coeff = params['pitch_system_mass_cost_coeff']
        
        #calculate system costs
        PitchSystemCost2015 = pitch_system_mass_cost_coeff * pitch_system_mass
        unknowns['pitch_system_cost'] = PitchSystemCost2015
        
#-------------------------------------------------------------------------------
class SpinnerCost2015(Component):

    def __init__(self):

        super(SpinnerCost2015, self).__init__()

        # variables
        self.add_param('spinner_mass', 0.0, desc='component mass', units='kg')
        self.add_param('spinner_mass_cost_coeff', 11.1, desc='spinner/nose cone mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('spinner_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        spinner_mass_cost_coeff = params['spinner_mass_cost_coeff']
        spinner_mass = params['spinner_mass']

        #calculate system costs
        SpinnerCost2015 = spinner_mass_cost_coeff * spinner_mass
        unknowns['spinner_cost'] = SpinnerCost2015

#-------------------------------------------------------------------------------
class HubSystemCostAdder2015(Component):

    def __init__(self):

        super(HubSystemCostAdder2015, self).__init__()

        # Inputs
        self.add_param('hub_cost',          0.0, units='USD', desc='Hub component cost')
        self.add_param('hub_mass',          0.0, units='kg',  desc='Hub component mass')
        self.add_param('pitch_system_cost', 0.0, units='USD', desc='Pitch system cost')
        self.add_param('pitch_system_mass', 0.0, units='kg',  desc='Pitch system mass')
        self.add_param('spinner_cost',      0.0, units='USD', desc='Spinner component cost')
        self.add_param('spinner_mass',      0.0, units='kg', desc='Spinner component mass')
        self.add_param('hub_assemblyCostMultiplier',    0.0, desc='Rotor assembly cost multiplier')
        self.add_param('hub_overheadCostMultiplier',    0.0, desc='Rotor overhead cost multiplier')
        self.add_param('hub_profitMultiplier',          0.0, desc='Rotor profit multiplier')
        self.add_param('hub_transportMultiplier',       0.0, desc='Rotor transport multiplier')
    
        # Outputs
        self.add_output('hub_system_mass',  0.0, units='kg',  desc='Mass of the hub system, including hub, spinner, and pitch system for the blades')
        self.add_output('hub_system_cost',  0.0, units='USD', desc='Overall wind sub-assembly capial costs including transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        hub_cost            = params['hub_cost']
        pitch_system_cost   = params['pitch_system_cost']
        spinner_cost        = params['spinner_cost']
        
        hub_mass            = params['hub_mass']
        pitch_system_mass   = params['pitch_system_mass']
        spinner_mass        = params['spinner_mass']
        
        hub_assemblyCostMultiplier  = params['hub_assemblyCostMultiplier']
        hub_overheadCostMultiplier  = params['hub_overheadCostMultiplier']
        hub_profitMultiplier        = params['hub_profitMultiplier']
        hub_transportMultiplier     = params['hub_transportMultiplier']

        # Updated calculations below to account for assembly, transport, overhead and profit
        unknowns['hub_system_mass'] = hub_mass + pitch_system_mass + spinner_mass
        partsCost = hub_cost + pitch_system_cost + spinner_cost
        unknowns['hub_system_cost'] = (1 + hub_transportMultiplier + hub_profitMultiplier) * ((1 + hub_overheadCostMultiplier + hub_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------
class RotorCostAdder2015(Component):
    """
    RotorCostAdder adds up individual rotor system and component costs to get overall rotor cost.
    """

    def __init__(self):
        
        super(RotorCostAdder2015, self).__init__()

        # Inputs
        self.add_param('blade_cost',        0.0, units='USD',   desc='Individual blade cost')
        self.add_param('blade_mass',        0.0, units='kg',    desc='Individual blade mass')
        self.add_param('hub_system_cost',   0.0, units='USD',   desc='Cost for hub system')
        self.add_param('hub_system_mass',   0.0, units='kg',    desc='Mass for hub system')
        self.add_param('blade_number',      3,                  desc='Number of rotor blades', pass_by_obj=True)
    
        # Outputs
        self.add_output('rotor_cost',       0.0, units='USD',   desc='Overall wind sub-assembly capial costs including transportation costs')
        self.add_output('rotor_mass_tcc',   0.0, units='kg',    desc='Rotor mass, including blades, pitch system, hub, and spinner')
        
    def solve_nonlinear(self, params, unknowns, resids):

        blade_cost      = params['blade_cost']
        blade_mass      = params['blade_mass']
        blade_number    = params['blade_number']
        hub_system_cost = params['hub_system_cost']
        hub_system_mass = params['hub_system_mass']

        unknowns['rotor_cost']      = blade_cost * blade_number + hub_system_cost
        unknowns['rotor_mass_tcc']  = blade_mass * blade_number + hub_system_mass

#-------------------------------------------------------------------------------


###### Nacelle
# -------------------------------------------------
class LowSpeedShaftCost2015(Component):

    def __init__(self):

        super(LowSpeedShaftCost2015, self).__init__()

        # variables
        self.add_param('lss_mass', 0.0, desc='component mass', units='kg') #mass input
        self.add_param('lss_mass_cost_coeff', 11.9, desc='low speed shaft mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('lss_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs') #initialize cost output

    def solve_nonlinear(self, params, unknowns, resids):

        lss_mass_cost_coeff = params['lss_mass_cost_coeff']
        lss_mass = params['lss_mass']

        # calculate component cost
        unknowns['lss_cost'] = lss_mass_cost_coeff * lss_mass

#-------------------------------------------------------------------------------
class BearingsCost2015(Component):

    def __init__(self):

        super(BearingsCost2015, self).__init__()

        # variables
        self.add_param('main_bearing_mass', 0.0, desc='component mass', units='kg') #mass input
        self.add_param('main_bearing_number', 2, desc='number of main bearings', pass_by_obj=True) #number of main bearings- defaults to 2
        self.add_param('bearings_mass_cost_coeff', 4.5, desc='main bearings mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('main_bearing_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        main_bearing_mass = params['main_bearing_mass']
        main_bearing_number = params['main_bearing_number']
        bearings_mass_cost_coeff = params['bearings_mass_cost_coeff']

        #calculate component cost 
        unknowns['main_bearing_cost'] = bearings_mass_cost_coeff * main_bearing_mass * main_bearing_number

#-------------------------------------------------------------------------------
class GearboxCost2015(Component):

    def __init__(self):

        super(GearboxCost2015, self).__init__()

        # variables
        self.add_param('gearbox_mass', 0.0, units='kg', desc='component mass')
        self.add_param('gearbox_mass_cost_coeff', 12.9, desc='gearbox mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('gearbox_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        gearbox_mass = params['gearbox_mass']
        gearbox_mass_cost_coeff = params['gearbox_mass_cost_coeff']

        unknowns['gearbox_cost'] = gearbox_mass_cost_coeff * gearbox_mass

#-------------------------------------------------------------------------------
class HighSpeedSideCost2015(Component):

    def __init__(self):
        
        super(HighSpeedSideCost2015, self).__init__()

        # variables
        self.add_param('hss_mass', 0.0, desc='component mass', units='kg')
        self.add_param('hss_mass_cost_coeff', 6.8, desc='high speed side mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('hss_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        hss_mass = params['hss_mass']
        hss_mass_cost_coeff = params['hss_mass_cost_coeff']
        
        unknowns['hss_cost'] = hss_mass_cost_coeff * hss_mass

#-------------------------------------------------------------------------------
class GeneratorCost2015(Component):

    def __init__(self):

        super(GeneratorCost2015, self).__init__()

        # variables
        self.add_param('generator_mass', 0.0, desc='component mass', units='kg')
        self.add_param('generator_mass_cost_coeff', 12.4, desc='generator mass cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('generator_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        generator_mass = params['generator_mass']
        generator_mass_cost_coeff = params['generator_mass_cost_coeff']
        
        unknowns['generator_cost'] = generator_mass_cost_coeff * generator_mass

#-------------------------------------------------------------------------------
class BedplateCost2015(Component):

    def __init__(self):
        
        super(BedplateCost2015, self).__init__()
        
        # variables
        self.add_param('bedplate_mass', 0.0, desc='component mass', units='kg')
        self.add_param('bedplate_mass_cost_coeff', 2.9, desc='bedplate mass-cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('bedplate_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        bedplate_mass = params['bedplate_mass']
        bedplate_mass_cost_coeff = params['bedplate_mass_cost_coeff']

        unknowns['bedplate_cost'] = bedplate_mass_cost_coeff * bedplate_mass

#---------------------------------------------------------------------------------
class YawSystemCost2015(Component):

    def __init__(self):

        super(YawSystemCost2015, self).__init__()

        # variables
        self.add_param('yaw_mass', 0.0, desc='component mass', units='kg')
        self.add_param('yaw_mass_cost_coeff', 8.3, desc='yaw system mass cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('yaw_system_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        yaw_mass = params['yaw_mass']
        yaw_mass_cost_coeff = params['yaw_mass_cost_coeff']
        
        unknowns['yaw_system_cost'] = yaw_mass_cost_coeff * yaw_mass

#---------------------------------------------------------------------------------
class VariableSpeedElecCost2015(Component):

    def __init__(self):

        super(VariableSpeedElecCost2015, self).__init__()

        # variables
        self.add_param('vs_electronics_mass', 0.0, desc='component mass', units='kg')
        self.add_param('vs_electronics_mass_cost_coeff', 18.8, desc='variable speed electronics mass cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('vs_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        vs_electronics_mass = params['vs_electronics_mass']
        vs_electronics_mass_cost_coeff = params['vs_electronics_mass_cost_coeff']

        unknowns['vs_cost'] = vs_electronics_mass_cost_coeff * vs_electronics_mass

#---------------------------------------------------------------------------------
class HydraulicCoolingCost2015(Component):

    def __init__(self):

        super(HydraulicCoolingCost2015, self).__init__()

        # variables
        self.add_param('hvac_mass', 0.0, desc='component mass', units='kg')
        self.add_param('hvac_mass_cost_coeff', 124.0, desc='hydraulic and cooling system mass cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('hvac_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        hvac_mass = params['hvac_mass']
        hvac_mass_cost_coeff = params['hvac_mass_cost_coeff']

        # calculate cost
        unknowns['hvac_cost'] = hvac_mass_cost_coeff * hvac_mass

#---------------------------------------------------------------------------------
class NacelleCoverCost2015(Component):

    def __init__(self):

        super(NacelleCoverCost2015, self).__init__()

        # variables
        self.add_param('cover_mass', 0.0, desc='component mass', units='kg')
        self.add_param('cover_mass_cost_coeff', 5.7, desc='nacelle cover mass cost coeff', units='USD/kg')
    
        # Outputs
        self.add_output('cover_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        cover_mass = params['cover_mass']
        cover_mass_cost_coeff = params['cover_mass_cost_coeff']

        unknowns['cover_cost'] = cover_mass_cost_coeff * cover_mass

#---------------------------------------------------------------------------------
class ElecConnecCost2015(Component):

    def __init__(self):

        super(ElecConnecCost2015, self).__init__()

        # variables
        self.add_param('machine_rating', 0.0, desc='machine rating', units='kW')
        self.add_param('elec_connec_machine_rating_cost_coeff', 41.85, units='USD/kW', desc='electrical connections cost coefficient per kW')
    
        # Outputs
        self.add_output('elec_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        machine_rating = params['machine_rating']
        elec_connec_machine_rating_cost_coeff = params['elec_connec_machine_rating_cost_coeff']

        unknowns['elec_cost'] = elec_connec_machine_rating_cost_coeff * machine_rating


#---------------------------------------------------------------------------------
class ControlsCost2015(Component):

    def __init__(self):

        super(ControlsCost2015, self).__init__()

        # variables
        self.add_param('machine_rating', 0.0, desc='machine rating', units='kW')
        self.add_param('controls_machine_rating_cost_coeff', 21.15, units='USD/kW', desc='controls cost coefficient per kW')
    
        # Outputs
        self.add_output('controls_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        machine_rating = params['machine_rating']
        coeff          = params['controls_machine_rating_cost_coeff']

        unknowns['controls_cost'] = machine_rating * coeff

#---------------------------------------------------------------------------------
class OtherMainframeCost2015(Component):

    def __init__(self):  

        super(OtherMainframeCost2015, self).__init__()

        # variables
        self.add_param('platforms_mass', 0.0, desc='component mass', units='kg')
        self.add_param('platforms_mass_cost_coeff', 17.1, desc='nacelle platforms mass cost coeff', units='USD/kg')
        self.add_param('crane', False, desc='flag for presence of onboard crane', pass_by_obj=True)
        self.add_param('crane_cost', 12000.0, desc='crane cost if present', units='USD')
        # self.add_param('bedplate_cost', 0.0, desc='component cost', units='USD')
        # self.add_param('base_hardware_cost_coeff', 0.7, desc='base hardware cost coeff based on bedplate cost')
    
        # Outputs
        self.add_output('other_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        platforms_mass = params['platforms_mass']
        platforms_mass_cost_coeff = params['platforms_mass_cost_coeff']
        crane = params['crane']
        crane_cost = params['crane_cost']
        # bedplate_cost = params['bedplate_cost']
        # base_hardware_cost_coeff = params['base_hardware_cost_coeff']

        # nacelle platform cost

        # crane cost
        if (crane):
            craneCost  = crane_cost
            craneMass  = 3e3
            NacellePlatformsCost = platforms_mass_cost_coeff * (platforms_mass - craneMass)
        else:
            craneCost  = 0.0
            NacellePlatformsCost = platforms_mass_cost_coeff * platforms_mass

        # base hardware cost
        #BaseHardwareCost = bedplate_cost * base_hardware_cost_coeff
    
        #aggregate all three mainframe costs
        unknowns['other_cost'] = NacellePlatformsCost + craneCost #+ BaseHardwareCost

#-------------------------------------------------------------------------------
class TransformerCost2015(Component):

    def __init__(self):

        super(TransformerCost2015, self).__init__()

        # variables
        self.add_param('transformer_mass', 0.0, desc='component mass', units='kg')
        self.add_param('transformer_mass_cost_coeff', 18.8, desc='transformer mass cost coeff', units='USD/kg') #mass-cost coeff with default from ppt
    
        # Outputs
        self.add_output('transformer_cost', 0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        transformer_mass = params['transformer_mass']
        transformer_mass_cost_coeff = params['transformer_mass_cost_coeff']
        
        unknowns['transformer_cost'] = transformer_mass_cost_coeff * transformer_mass

#-------------------------------------------------------------------------------
class NacelleSystemCostAdder2015(Component):

    def __init__(self):
        
        super(NacelleSystemCostAdder2015, self).__init__()

        # variables
        self.add_param('lss_cost',          0.0, units='USD', desc='Component cost')
        self.add_param('lss_mass',          0.0, units='kg',  desc='Component mass')
        self.add_param('main_bearing_cost', 0.0, units='USD', desc='Component cost')
        self.add_param('main_bearing_mass', 0.0, units='kg',  desc='Component mass')
        self.add_param('gearbox_cost',      0.0, units='USD', desc='Component cost')
        self.add_param('gearbox_mass',      0.0, units='kg',  desc='Component mass')
        self.add_param('hss_cost',          0.0, units='USD', desc='Component cost')
        self.add_param('hss_mass',          0.0, units='kg',  desc='Component mass')
        self.add_param('generator_cost',    0.0, units='USD', desc='Component cost')
        self.add_param('generator_mass',    0.0, units='kg',  desc='Component mass')
        self.add_param('bedplate_cost',     0.0, units='USD', desc='Component cost')
        self.add_param('bedplate_mass',     0.0, units='kg',  desc='Component mass')
        self.add_param('yaw_system_cost',   0.0, units='USD', desc='Component cost')
        self.add_param('yaw_mass',          0.0, units='kg',  desc='Component mass')
        self.add_param('vs_cost',           0.0, units='USD', desc='Component cost')
        self.add_param('vs_mass',           0.0, units='kg',  desc='Component mass')
        self.add_param('hvac_cost',         0.0, units='USD', desc='Component cost')
        self.add_param('hvac_mass',         0.0, units='kg',  desc='Component mass')
        self.add_param('cover_cost',        0.0, units='USD', desc='Component cost')
        self.add_param('cover_mass',        0.0, units='kg',  desc='Component mass')
        self.add_param('elec_cost',         0.0, units='USD', desc='Component cost')
        self.add_param('controls_cost',     0.0, units='USD', desc='Component cost')
        self.add_param('other_cost',        0.0, units='USD', desc='Component cost')
        self.add_param('transformer_cost',  0.0, units='USD', desc='Component cost')
        self.add_param('transformer_mass',  0.0, units='kg',  desc='Component mass')
        self.add_param('main_bearing_number', 2, desc ='number of bearings', pass_by_obj=True)
        
        #multipliers
        self.add_param('nacelle_assemblyCostMultiplier', 0.0, desc='nacelle assembly cost multiplier')
        self.add_param('nacelle_overheadCostMultiplier', 0.0, desc='nacelle overhead cost multiplier')
        self.add_param('nacelle_profitMultiplier',       0.0, desc='nacelle profit multiplier')
        self.add_param('nacelle_transportMultiplier',    0.0, desc='nacelle transport multiplier')
    
        # returns
        self.add_output('nacelle_cost', 0.0, units='USD', desc='component cost')
        self.add_output('nacelle_mass', 0.0, units='kg',  desc='Nacelle mass, with all nacelle components, without the rotor')

    def solve_nonlinear(self, params, unknowns, resids):

        lss_cost            = params['lss_cost']
        main_bearing_cost   = params['main_bearing_cost']
        gearbox_cost        = params['gearbox_cost']
        hss_cost            = params['hss_cost']
        generator_cost      = params['generator_cost']
        bedplate_cost       = params['bedplate_cost']
        yaw_system_cost     = params['yaw_system_cost']
        vs_cost             = params['vs_cost']
        hvac_cost           = params['hvac_cost']
        cover_cost          = params['cover_cost']
        elec_cost           = params['elec_cost']
        controls_cost       = params['controls_cost']
        other_cost          = params['other_cost']
        transformer_cost    = params['transformer_cost']
        
        lss_mass            = params['lss_mass']
        main_bearing_mass   = params['main_bearing_mass']
        gearbox_mass        = params['gearbox_mass']
        hss_mass            = params['hss_mass']
        generator_mass      = params['generator_mass']
        bedplate_mass       = params['bedplate_mass']
        yaw_mass            = params['yaw_mass']
        vs_mass             = params['vs_mass']
        hvac_mass           = params['hvac_mass']
        cover_mass          = params['cover_mass']
        transformer_mass    = params['transformer_mass']
        
        main_bearing_number = params['main_bearing_number']

        nacelle_assemblyCostMultiplier  = params['nacelle_assemblyCostMultiplier']
        nacelle_overheadCostMultiplier  = params['nacelle_overheadCostMultiplier']
        nacelle_profitMultiplier        = params['nacelle_profitMultiplier']
        nacelle_transportMultiplier     = params['nacelle_transportMultiplier']        

        #apply multipliers for assembly, transport, overhead, and profits
        unknowns['nacelle_mass'] = lss_mass + main_bearing_number * main_bearing_mass + gearbox_mass + hss_mass + generator_mass + bedplate_mass + yaw_mass + vs_mass + hvac_mass + cover_mass + transformer_mass
        partsCost = lss_cost + main_bearing_number * main_bearing_cost + gearbox_cost + hss_cost + generator_cost + bedplate_cost + yaw_system_cost + vs_cost + hvac_cost + cover_cost + elec_cost + controls_cost + other_cost + transformer_cost
        unknowns['nacelle_cost'] = (1 + nacelle_transportMultiplier + nacelle_profitMultiplier) * ((1 + nacelle_overheadCostMultiplier + nacelle_assemblyCostMultiplier) * partsCost)

###### Tower
#-------------------------------------------------------------------------------
class TowerCost2015(Component):

    def __init__(self):
      
        super(TowerCost2015, self).__init__()

        # variables
        self.add_param('tower_mass',            0.0, units='kg',     desc='tower mass')
        self.add_param('tower_mass_cost_coeff', 2.9, units='USD/kg', desc='tower mass-cost coeff') #mass-cost coeff with default from ppt
        self.add_param('tower_cost_external',   0.0, units='USD',    desc='Tower cost computed by TowerSE')
        
        # Outputs
        self.add_output('tower_parts_cost',     0.0, units='USD', desc='Overall wind turbine component capial costs excluding transportation costs')

    def solve_nonlinear(self, params, unknowns, resids):

        tower_mass = params['tower_mass']
        tower_mass_cost_coeff = params['tower_mass_cost_coeff']
        
        # calculate component cost
        if params['tower_cost_external'] < 1.:
            unknowns['tower_parts_cost'] = tower_mass_cost_coeff * tower_mass
        else:
            unknowns['tower_parts_cost'] = params['tower_cost_external']
        
        
#-------------------------------------------------------------------------------
class TowerCostAdder2015(Component):

    def __init__(self):

        super(TowerCostAdder2015, self).__init__()

        # variables
        self.add_param('tower_parts_cost', 0.0, units='USD', desc='component cost')
      
        # multipliers
        self.add_param('tower_assemblyCostMultiplier', 0.0, desc='tower assembly cost multiplier')
        self.add_param('tower_overheadCostMultiplier', 0.0, desc='tower overhead cost multiplier')
        self.add_param('tower_profitMultiplier', 0.0, desc='tower profit cost multiplier')
        self.add_param('tower_transportMultiplier', 0.0, desc='tower transport cost multiplier')
        
        # returns
        self.add_output('tower_cost', 0.0, units='USD', desc='component cost') 

    def solve_nonlinear(self, params, unknowns, resids):

        tower_parts_cost = params['tower_parts_cost']

        tower_assemblyCostMultiplier = params['tower_assemblyCostMultiplier']
        tower_overheadCostMultiplier = params['tower_overheadCostMultiplier']
        tower_profitMultiplier = params['tower_profitMultiplier']
        tower_transportMultiplier = params['tower_transportMultiplier']

        partsCost = tower_parts_cost
        unknowns['tower_cost'] = (1 + tower_transportMultiplier + tower_profitMultiplier) * ((1 + tower_overheadCostMultiplier + tower_assemblyCostMultiplier) * partsCost)

#-------------------------------------------------------------------------------
class TurbineCostAdder2015(Component):

    def __init__(self):

        super(TurbineCostAdder2015, self).__init__()

        # Variables
        self.add_param('rotor_cost',        0.0, units='USD',   desc='Rotor cost')
        self.add_param('rotor_mass_tcc',    0.0, units='kg',    desc='Rotor mass')
        self.add_param('nacelle_cost',      0.0, units='USD',   desc='Nacelle cost')
        self.add_param('nacelle_mass',      0.0, units='kg',    desc='Nacelle mass')
        self.add_param('tower_cost',        0.0, units='USD',   desc='Tower cost')
        self.add_param('tower_mass',        0.0, units='kg',    desc='Tower mass')
        self.add_param('machine_rating',    0.0, units='kW',    desc='Machine rating')
    
        # parameters
        self.add_param('turbine_assemblyCostMultiplier',    0.0, desc='Turbine multiplier for assembly cost in manufacturing')
        self.add_param('turbine_overheadCostMultiplier',    0.0, desc='Turbine multiplier for overhead')
        self.add_param('turbine_profitMultiplier',          0.0, desc='Turbine multiplier for profit markup')
        self.add_param('turbine_transportMultiplier',       0.0, desc='Turbine multiplier for transport costs')
    
        # Outputs
        self.add_output('turbine_mass',     0.0, units='kg',    desc='Turbine total mass, without foundation')
        self.add_output('turbine_cost',     0.0, units='USD',   desc='Overall wind turbine capital costs including transportation costs')
        self.add_output('turbine_cost_kW',  0.0, units='USD/kW',desc='Overall wind turbine capial costs including transportation costs')
        
    def solve_nonlinear(self, params, unknowns, resids):

        rotor_cost      = params['rotor_cost']
        nacelle_cost    = params['nacelle_cost']
        tower_cost      = params['tower_cost']
        
        rotor_mass_tcc  = params['rotor_mass_tcc']
        nacelle_mass    = params['nacelle_mass']
        tower_mass      = params['tower_mass']
        
        turbine_assemblyCostMultiplier = params['turbine_assemblyCostMultiplier']
        turbine_overheadCostMultiplier = params['turbine_overheadCostMultiplier']
        turbine_profitMultiplier = params['turbine_profitMultiplier']
        turbine_transportMultiplier = params['turbine_transportMultiplier']

        partsCost = rotor_cost + nacelle_cost + tower_cost
        
        
        unknowns['turbine_mass']    =  rotor_mass_tcc + nacelle_mass + tower_mass
        unknowns['turbine_cost']    = (1 + turbine_transportMultiplier + turbine_profitMultiplier) * ((1 + turbine_overheadCostMultiplier + turbine_assemblyCostMultiplier) * partsCost)
        unknowns['turbine_cost_kW'] = unknowns['turbine_cost'] / params['machine_rating']

class Outputs2Screen(Component):
    def __init__(self, verbosity):
        super(Outputs2Screen, self).__init__()
        
        self.add_param('blade_cost',       0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('blade_mass',       0.0,  units='kg',  desc='Blade mass')
        self.add_param('hub_cost',         0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('hub_mass',         0.0,  units='kg',  desc='Hub mass')
        self.add_param('pitch_system_cost',       0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('pitch_system_mass',0.0,  units='kg',  desc='Pitch system mass')
        self.add_param('spinner_cost',     0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('spinner_mass',     0.0,  units='kg',  desc='Spinner mass')
        self.add_param('lss_cost',         0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('lss_mass',         0.0,  units='kg',  desc='LSS mass')
        self.add_param('main_bearing_cost',0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('main_bearing_mass',0.0,  units='kg',  desc='Main bearing mass')
        self.add_param('gearbox_cost',     0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('gearbox_mass',     0.0,  units='kg',  desc='LSS mass')
        self.add_param('hss_cost',         0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('hss_mass',         0.0,  units='kg',  desc='HSS mass')
        self.add_param('generator_cost',   0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('generator_mass',   0.0,  units='kg',  desc='Generator mass')
        self.add_param('bedplate_cost',    0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('bedplate_mass',    0.0,  units='kg',  desc='Bedplate mass')
        self.add_param('yaw_system_cost',  0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('yaw_mass',         0.0,  units='kg',  desc='Yaw system mass')
        self.add_param('hvac_cost',        0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('hvac_mass',        0.0,  units='kg',  desc='HVAC mass')
        self.add_param('cover_cost',       0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('cover_mass',       0.0,  units='kg',  desc='Cover mass')
        self.add_param('elec_cost',        0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('controls_cost',    0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('other_cost',       0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('transformer_cost', 0.0,  units='USD', desc='Overall wind turbine component capital costs excluding transportation costs')
        self.add_param('transformer_mass', 0.0,  units='kg',  desc='Transformer mass')
                                           
        self.add_param('rotor_cost',       0.0,  units='USD', desc='Overall wind turbine rotor capital costs')
        self.add_param('rotor_mass_tcc',   0.0,  units='kg',  desc='Rotor mass')
        self.add_param('nacelle_cost',     0.0,  units='USD', desc='Overall wind turbine nacelle capital costs')
        self.add_param('nacelle_mass',     0.0,  units='kg',  desc='Nacelle mass')
        self.add_param('tower_cost',       0.0,  units='USD', desc='Overall wind turbine tower capital costs')
        self.add_param('tower_mass',       0.0,  units='kg',  desc='Tower mass')
        self.add_param('turbine_cost',     0.0,  units='USD', desc='Overall wind turbine capital costs including transportation costs')
        self.add_param('turbine_mass',     0.0,  units='kg',  desc='Turbine mass')
        
        self.verbosity = verbosity
        
        
    def solve_nonlinear(self, params, unknowns, resids):        
        
        if self.verbosity == True:
        
            
            print('################################################')
            print('Computation of costs of the main turbine components from TurbineCostSE')
            print('Blade cost              %.3f k USD       mass %.3f kg' % (params['blade_cost'] * 1.e-003,        params['blade_mass']))
            print('Pitch system cost       %.3f k USD       mass %.3f kg' % (params['pitch_system_cost'] * 1.e-003, params['pitch_system_mass']))
            print('Hub cost                %.3f k USD       mass %.3f kg' % (params['hub_cost'] * 1.e-003,          params['hub_mass']))
            print('Spinner cost            %.3f k USD       mass %.3f kg' % (params['spinner_cost'] * 1.e-003,      params['spinner_mass']))
            print('------------------------------------------------')
            print('Rotor cost              %.3f k USD       mass %.3f kg' % (params['rotor_cost'] * 1.e-003,        params['rotor_mass_tcc']))
            print('')
            print('LSS cost                %.3f k USD       mass %.3f kg' % (params['lss_cost'] * 1.e-003,          params['lss_mass']))
            print('Main bearing cost       %.3f k USD       mass %.3f kg' % (params['main_bearing_cost'] * 1.e-003, params['main_bearing_mass']))
            print('Gearbox cost            %.3f k USD       mass %.3f kg' % (params['gearbox_cost'] * 1.e-003,      params['gearbox_mass']))
            print('HSS cost                %.3f k USD       mass %.3f kg' % (params['hss_cost'] * 1.e-003,          params['hss_mass']))
            print('Generator cost          %.3f k USD       mass %.3f kg' % (params['generator_cost'] * 1.e-003,    params['generator_mass']))
            print('Bedplate cost           %.3f k USD       mass %.3f kg' % (params['bedplate_cost'] * 1.e-003,     params['bedplate_mass']))
            print('Yaw system cost         %.3f k USD       mass %.3f kg' % (params['yaw_system_cost'] * 1.e-003,   params['yaw_mass']))
            print('HVAC cost               %.3f k USD       mass %.3f kg' % (params['hvac_cost'] * 1.e-003,         params['hvac_mass']))
            print('Nacelle cover cost      %.3f k USD       mass %.3f kg' % (params['cover_cost'] * 1.e-003,        params['cover_mass']))
            print('Electr connection cost  %.3f k USD'                    % (params['elec_cost'] * 1.e-003))
            print('Controls cost           %.3f k USD'                    % (params['controls_cost'] * 1.e-003))
            print('Other main frame cost   %.3f k USD'                    % (params['other_cost'] * 1.e-003))
            print('Transformer cost        %.3f k USD       mass %.3f kg' % (params['transformer_cost'] * 1.e-003,  params['transformer_mass']))
            print('------------------------------------------------')
            print('Nacelle cost            %.3f k USD       mass %.3f kg' % (params['nacelle_cost'] * 1.e-003,      params['nacelle_mass']))
            print('')
            print('Tower cost              %.3f k USD       mass %.3f kg' % (params['tower_cost'] * 1.e-003,        params['tower_mass']))
            print('------------------------------------------------')
            print('------------------------------------------------')
            print('Turbine cost            %.3f k USD       mass %.3f kg' % (params['turbine_cost'] * 1.e-003,      params['turbine_mass']))
            print('################################################')
                
    

#-------------------------------------------------------------------------------
class Turbine_CostsSE_2015(Group):

    def __init__(self, verbosity = False):
        super(Turbine_CostsSE_2015, self).__init__()

        self.add('blade_mass_cost_coeff',                 IndepVarComp('blade_mass_cost_coeff',         val=14.6),  promotes=['*'])
        self.add('hub_mass_cost_coeff',                   IndepVarComp('hub_mass_cost_coeff',           val=3.9),   promotes=['*'])
        self.add('pitch_system_mass_cost_coeff',          IndepVarComp('pitch_system_mass_cost_coeff',  val=22.1),  promotes=['*'])
        self.add('spinner_mass_cost_coeff',               IndepVarComp('spinner_mass_cost_coeff',       val=11.1),  promotes=['*'])
        self.add('lss_mass_cost_coeff',                   IndepVarComp('lss_mass_cost_coeff',           val=11.9),  promotes=['*'])
        self.add('bearings_mass_cost_coeff',              IndepVarComp('bearings_mass_cost_coeff',      val=4.5),   promotes=['*'])
        self.add('gearbox_mass_cost_coeff',               IndepVarComp('gearbox_mass_cost_coeff',       val=12.9),  promotes=['*'])
        self.add('hss_mass_cost_coeff',                   IndepVarComp('hss_mass_cost_coeff',           val=6.8),   promotes=['*'])
        self.add('generator_mass_cost_coeff',             IndepVarComp('generator_mass_cost_coeff',     val=12.4),  promotes=['*'])
        self.add('bedplate_mass_cost_coeff',              IndepVarComp('bedplate_mass_cost_coeff',      val=2.9),   promotes=['*'])
        self.add('yaw_mass_cost_coeff',                   IndepVarComp('yaw_mass_cost_coeff',           val=8.3),   promotes=['*'])
        self.add('vs_electronics_mass_cost_coeff',        IndepVarComp('vs_electronics_mass_cost_coeff',val=18.8),  promotes=['*'])
        self.add('hvac_mass_cost_coeff',                  IndepVarComp('hvac_mass_cost_coeff',          val=124.0), promotes=['*'])
        self.add('cover_mass_cost_coeff',                 IndepVarComp('cover_mass_cost_coeff',         val=5.7),   promotes=['*'])
        self.add('elec_connec_machine_rating_cost_coeff', IndepVarComp('elec_connec_machine_rating_cost_coeff',val=41.85), promotes=['*'])
        self.add('platforms_mass_cost_coeff',             IndepVarComp('platforms_mass_cost_coeff',     val=17.1),  promotes=['*'])
        self.add('base_hardware_cost_coeff',              IndepVarComp('base_hardware_cost_coeff',      val=0.7),   promotes=['*'])
        self.add('transformer_mass_cost_coeff',           IndepVarComp('transformer_mass_cost_coeff',   val=18.8),  promotes=['*'])
        self.add('tower_mass_cost_coeff',                 IndepVarComp('tower_mass_cost_coeff',         val=2.9),   promotes=['*'])
        self.add('controls_machine_rating_cost_coeff',    IndepVarComp('controls_machine_rating_cost_coeff', val=21.15), promotes=['*'])
        self.add('crane_cost',                            IndepVarComp('crane_cost',                    val=12e3),  promotes=['*'])
        
        self.add('hub_assemblyCostMultiplier',            IndepVarComp('hub_assemblyCostMultiplier',    val=0.0), promotes=['*'])
        self.add('hub_overheadCostMultiplier',            IndepVarComp('hub_overheadCostMultiplier',    val=0.0), promotes=['*'])
        self.add('nacelle_assemblyCostMultiplier',        IndepVarComp('nacelle_assemblyCostMultiplier',val=0.0), promotes=['*'])
        self.add('nacelle_overheadCostMultiplier',        IndepVarComp('nacelle_overheadCostMultiplier',val=0.0), promotes=['*'])
        self.add('tower_assemblyCostMultiplier',          IndepVarComp('tower_assemblyCostMultiplier',  val=0.0), promotes=['*'])
        self.add('tower_overheadCostMultiplier',          IndepVarComp('tower_overheadCostMultiplier',  val=0.0), promotes=['*'])
        self.add('turbine_assemblyCostMultiplier',        IndepVarComp('turbine_assemblyCostMultiplier',val=0.0), promotes=['*'])
        self.add('turbine_overheadCostMultiplier',        IndepVarComp('turbine_overheadCostMultiplier',val=0.0), promotes=['*'])
        self.add('hub_profitMultiplier',                  IndepVarComp('hub_profitMultiplier',          val=0.0), promotes=['*'])
        self.add('nacelle_profitMultiplier',              IndepVarComp('nacelle_profitMultiplier',      val=0.0), promotes=['*'])
        self.add('tower_profitMultiplier',                IndepVarComp('tower_profitMultiplier',        val=0.0), promotes=['*'])
        self.add('turbine_profitMultiplier',              IndepVarComp('turbine_profitMultiplier',      val=0.0), promotes=['*'])
        self.add('hub_transportMultiplier',               IndepVarComp('hub_transportMultiplier',       val=0.0), promotes=['*'])
        self.add('nacelle_transportMultiplier',           IndepVarComp('nacelle_transportMultiplier',   val=0.0), promotes=['*'])
        self.add('tower_transportMultiplier',             IndepVarComp('tower_transportMultiplier',     val=0.0), promotes=['*'])
        self.add('turbine_transportMultiplier',           IndepVarComp('turbine_transportMultiplier',   val=0.0), promotes=['*'])

        
        self.add('blade_c'       , BladeCost2015(),         promotes=['*'])
        self.add('hub_c'         , HubCost2015(),           promotes=['*'])
        self.add('pitch_c'       , PitchSystemCost2015(),   promotes=['*'])
        self.add('spinner_c'     , SpinnerCost2015(),       promotes=['*'])
        self.add('hub_adder'     , HubSystemCostAdder2015(),promotes=['*'])
        self.add('rotor_adder'   , RotorCostAdder2015(),    promotes=['*'])
        self.add('lss_c'         , LowSpeedShaftCost2015(), promotes=['*'])
        self.add('bearing_c'     , BearingsCost2015(),      promotes=['*'])
        self.add('gearbox_c'     , GearboxCost2015(),       promotes=['*'])
        self.add('hss_c'         , HighSpeedSideCost2015(), promotes=['*'])
        self.add('generator_c'   , GeneratorCost2015(),     promotes=['*'])
        self.add('bedplate_c'    , BedplateCost2015(),      promotes=['*'])
        self.add('yaw_c'         , YawSystemCost2015(),     promotes=['*'])
        self.add('hvac_c'        , HydraulicCoolingCost2015(), promotes=['*'])
        self.add('controls_c'    , ControlsCost2015(),      promotes=['*'])
        self.add('vs_c'          , VariableSpeedElecCost2015(), promotes=['*'])
        self.add('elec_c'        , ElecConnecCost2015(),    promotes=['*'])
        self.add('cover_c'       , NacelleCoverCost2015(),  promotes=['*'])
        self.add('other_c'       , OtherMainframeCost2015(),promotes=['*'])
        self.add('transformer_c' , TransformerCost2015(),   promotes=['*'])
        self.add('nacelle_adder' , NacelleSystemCostAdder2015(), promotes=['*'])
        self.add('tower_c'       , TowerCost2015(),         promotes=['*'])
        self.add('tower_adder'   , TowerCostAdder2015(),    promotes=['*'])
        self.add('turbine_c'     , TurbineCostAdder2015(),  promotes=['*'])
        self.add('outputs'       , Outputs2Screen(verbosity), promotes=['*'])

#-------------------------------------------------------------------------------
def example():

    # simple test of module
    turbine = Turbine_CostsSE_2015()
    prob = Problem(turbine)
    prob.setup()

    prob['blade_mass']          = 17650.67  # inline with the windpact estimates
    prob['hub_mass']            = 31644.5
    prob['pitch_system_mass']   = 17004.0
    prob['spinner_mass']        = 1810.5
    prob['lss_mass']            = 31257.3
    #bearingsMass'] = 9731.41
    prob['main_bearing_mass']   = 9731.41 / 2
    prob['gearbox_mass']        = 30237.60
    prob['hss_mass']            = 1492.45
    prob['generator_mass']      = 16699.85
    prob['bedplate_mass']       = 93090.6
    prob['yaw_mass']            = 11878.24
    prob['tower_mass']          = 434559.0
    prob['vs_electronics_mass'] = 1000.
    prob['hvac_mass']           = 1000.
    prob['cover_mass']          = 1000.
    prob['platforms_mass']      = 1000.
    prob['transformer_mass']    = 1000.

    # other inputs
    prob['machine_rating']      = 5000.0
    prob['blade_number']        = 3
    prob['crane']               = True
    prob['main_bearing_number'] = 2

    prob.run()

    #print('The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are')
    for io in turbine.unknowns:
        print(io + ' ' + str(turbine.unknowns[io]))


if __name__ == "__main__":

    example()
