"""
tcc_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree, Enum

from fusedwind.plant_cost.fused_tcc import BaseTurbineCostModel, BaseTCCAggregator, configure_base_tcc
from fusedwind.interface import implement_base

from turbine_costsse_2015 import Turbine_CostsSE_2015

# --------------------------------------------------------------------
class BladeMass(Component):
  
    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    turbine_class = Enum('I', ('I', 'II/III', 'User Exponent'), iotype = 'in', desc='turbine class')
    blade_has_carbon = Bool(False, iotype='in', desc= 'does the blade have carbon?') #default to doesn't have carbon
    blade_mass_coefficient = Float(0.5, iotype='in', desc= 'A in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    rotor_diameter_denominator = Float(2.0, iotype='in', desc= 'B in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    blade_user_exponent = Float(2.5, iotype='in', desc='optional user-entered exponent for the blade mass equation')
    
    # Outputs
    blade_mass = Float(units='kg', iotype='out', desc= 'component mass [kg]')
  
    def execute(self):
    
        # select the exponent for the blade mass equation
        exponent = 0.0
        if self.turbine_class == 'I':
            if self.blade_has_carbon:
              exponent = 2.47
            else:
              exponent = 2.54
        elif self.turbine_class == 'II/III':
            if self.blade_has_carbon:
              exponent = 2.44
            else:
              exponent = 2.50
        else:
            exponent = self.blade_user_exponent
        
        # calculate the blade mass
        self.blade_mass = self.blade_mass_coefficient * (self.rotor_diameter / self.rotor_diameter_denominator)**exponent
      
  # --------------------------------------------------------------------
class HubMass(Component):
  
    # Variables
    blade_mass = Float(units='kg', iotype='in', desc= 'component mass [kg]')
    hub_mass_coeff = Float(2.3, iotype='in', desc= 'A in the hub mass equation: A*blade_mass + B') #default from ppt
    hub_mass_intercept = Float(1320., iotype='in', desc= 'B in the hub mass equation: A*blade_mass + B') #default from ppt
    
    # Outputs
    hub_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
  
    def execute(self):
      
        # calculate the hub mass
        self.hub_mass = self.hub_mass_coeff * self.blade_mass + self.hub_mass_intercept

# --------------------------------------------------------------------
class PitchSystemMass(Component):
  
    # Variables
    blade_mass = Float(units='kg', iotype='in', desc= 'component mass [kg]')
    blade_number = Int(iotype='in', desc='number of rotor blades')
    pitch_bearing_mass_coeff = Float(0.1295, iotype='in', desc='A in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    pitch_bearing_mass_intercept = Float(491.31, iotype='in', desc='B in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    bearing_housing_percent = Float(.3280, iotype='in', desc='bearing housing percentage (in decimal form: ex 10% is 0.10)') #default from old CSM
    mass_sys_offset = Float(555.0, iotype='in', desc='mass system offset') #default from old CSM
    
    # Outputs
    pitch_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate the hub mass
        pitchBearingMass = self.pitch_bearing_mass_coeff * self.blade_mass * self.blade_number + self.pitch_bearing_mass_intercept
        self.pitch_system_mass = pitchBearingMass * (1 + self.bearing_housing_percent) + self.mass_sys_offset

# --------------------------------------------------------------------
class SpinnerMass(Component):
  
    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    spinner_mass_coeff = Float(15.5, iotype='in', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    spinner_mass_intercept = Float(-980.0, iotype='in', desc= 'B in the spinner mass equation: A*rotor_diameter + B')
    
    # Outputs
    spinner_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate the spinner mass
        self.spinner_mass = self.spinner_mass_coeff * self.rotor_diameter + self.spinner_mass_intercept

# --------------------------------------------------------------------
class LowSpeedShaftMass(Component):
  
    # Variables
    blade_mass = Float(0.0, units='kg', iotype='in', desc='mass for a single wind turbine blade')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    lss_mass_coeff = Float(13., iotype='in', desc='A in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_exp = Float(0.65, iotype='in', desc='exp in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_intercept = Float(775., iotype='in', desc='B in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    
    # Outputs
    low_speed_shaft_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate the lss mass
        self.low_speed_shaft_mass = self.lss_mass_coeff * (self.blade_mass * self.machine_rating/1000.)**self.lss_mass_exp + self.lss_mass_intercept

# --------------------------------------------------------------------
class BearingMass(Component):
  
    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    bearing_mass_coeff = Float(0.0001, iotype='in', desc= 'A in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
    bearing_mass_exp = Float(3.5, iotype='in', desc= 'exp in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
    
    # Outputs
    main_bearing_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculates the mass of a SINGLE bearing
        self.main_bearing_mass = self.bearing_mass_coeff * self.rotor_diameter**self.bearing_mass_exp

# --------------------------------------------------------------------
class GearboxMass(Component):
  
    # Variables
    rotor_torque = Float(iotype='in', units='N * m', desc = 'torque from rotor at rated power') #JMF do we want this default?
    gearbox_mass_coeff = Float(113., iotype='in', desc= 'A in the gearbox mass equation: A*rotor_torque^exp')
    gearbox_mass_exp = Float(0.71, iotype='in', desc= 'exp in the gearbox mass equation: A*rotor_torque^exp')
    
    # Outputs
    gearbox_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
      
        # calculate the gearbox mass
        self.gearbox_mass = self.gearbox_mass_coeff * (self.rotor_torque/1000.0)**self.gearbox_mass_exp

# --------------------------------------------------------------------
class HighSpeedSideMass(Component):
  
    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    hss_mass_coeff = Float(0.19894, iotype='in', desc= 'NREL CSM hss equation; removing intercept since it is negligible')
    
    # Outputs
    high_speed_side_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
        
        # TODO: this is in DriveSE; replace this with code in DriveSE and have DriveSE use this code??
        self.high_speed_side_mass = self.hss_mass_coeff * self.machine_rating

# --------------------------------------------------------------------
class GeneratorMass(Component):
  
    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    generator_mass_coeff = Float(2300., iotype='in', desc= 'A in the generator mass equation: A*rated_power + B') #default from ppt
    generator_mass_intercept = Float(3400., iotype='in', desc= 'B in the generator mass equation: A*rated_power + B') #default from ppt
    
    # Outputs
    generator_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate the generator mass
        self.generator_mass = self.generator_mass_coeff * self.machine_rating/1000. + self.generator_mass_intercept

# --------------------------------------------------------------------
class BedplateMass(Component):
  
    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    bedplate_mass_exp = Float(2.2, iotype='in', desc= 'exp in the bedplate mass equation: rotor_diameter^exp')
    
    # Outputs
    bedplate_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
      
        # calculate the bedplate mass
        self.bedplate_mass = self.rotor_diameter**self.bedplate_mass_exp

# --------------------------------------------------------------------
class YawSystemMass(Component):
  
    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    yaw_mass_coeff = Float(0.0009, iotype='in', desc= 'A in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
    yaw_mass_exp = Float(3.314, iotype='in', desc= 'exp in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
    
    # Outputs
    yaw_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate yaw system mass #TODO - 50% adder for non-bearing mass
        self.yaw_system_mass = 1.5 * (self.yaw_mass_coeff * self.rotor_diameter ** self.yaw_mass_exp) #JMF do we really want to expose all these?

#TODO: no variable speed mass; ignore for now

# --------------------------------------------------------------------
class HydraulicCoolingMass(Component):
  
    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    hvac_mass_coeff = Float(0.08, iotype='in', desc= 'hvac linear coefficient') #NREL CSM
    
    # Outputs
    hydraulic_cooling_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate hvac system mass
        self.hydraulic_cooling_mass = self.hvac_mass_coeff * self.machine_rating

# --------------------------------------------------------------------
class NacelleCoverMass(Component):
  
    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    cover_mass_coeff = Float(1.2817, iotype='in', units='USD/kW', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    cover_mass_intercept = Float(428.19, iotype='in', units='USD', desc= 'B in the spinner mass equation: A*rotor_diameter + B')
    
    # Outputs
    nacelle_cover_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate nacelle cover mass
        self.nacelle_cover_mass = self.cover_mass_coeff * self.machine_rating + self.cover_mass_intercept

# TODO: ignoring controls and electronics mass for now

# --------------------------------------------------------------------
class OtherMainframeMass(Component):
    # nacelle platforms, service crane, base hardware
    
    # Variables
    bedplate_mass = Float(iotype='in', units='kg', desc='component mass [kg]')
    nacelle_platforms_mass_coeff = Float(0.125, iotype='in', units = 'USD/kg', desc='nacelle platforms mass coefficient as a function of bedplate mass [kg/kg]') #default from old CSM
    crane = Bool(False, iotype='in', desc='flag for presence of onboard crane')
    crane_weight = Float(3000., iotype='in', units='kg', desc='weight of onboard crane')
    #TODO: there is no base hardware mass model in the old model. Cost is not dependent on mass.
    
    # Outputs
    other_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
    
        # calculate nacelle cover mass           
        nacelle_platforms_mass = self.nacelle_platforms_mass_coeff * self.bedplate_mass

        # --- crane ---        
        if (self.crane):
            crane_mass =  self.crane_weight
        else:
            crane_mass = 0.  
        
        self.other_mass = nacelle_platforms_mass + crane_mass

# --------------------------------------------------------------------
class TransformerMass(Component):
  
    # Variables
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    transformer_mass_coeff = Float(1915., iotype='in', desc= 'A in the transformer mass equation: A*rated_power + B') #default from ppt
    transformer_mass_intercept = Float(1910., iotype='in', desc= 'B in the transformer mass equation: A*rated_power + B') #default from ppt
    
    # Outputs
    transformer_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
      
      # calculate the transformer mass
      self.transformer_mass = self.transformer_mass_coeff * self.machine_rating/1000. + self.transformer_mass_intercept

# --------------------------------------------------------------------
class TowerMass(Component):
  
    # Variables
    hub_height = Float(units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')
    tower_mass_coeff = Float(19.828, iotype='in', desc= 'A in the tower mass equation: A*hub_height + B') #default from ppt
    tower_mass_exp = Float(2.0282, iotype='in', desc= 'B in the tower mass equation: A*hub_height + B') #default from ppt
    
    # Outputs
    tower_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    
    def execute(self):
        
        # calculate the tower mass
        self.tower_mass = self.tower_mass_coeff * self.hub_height ** self.tower_mass_exp
 

# Turbine mass adder
class turbine_mass_adder(Component):
    
    # Inputs
    # rotor
    blade_mass = Float(units='kg', iotype='in', desc= 'component mass [kg]')
    hub_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    pitch_system_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    spinner_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    # nacelle
    low_speed_shaft_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    main_bearing_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    gearbox_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    high_speed_side_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    generator_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    bedplate_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    yaw_system_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    hydraulic_cooling_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    nacelle_cover_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    other_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    transformer_mass = Float(units='kg', iotype='in', desc='component mass [kg]')
    # tower
    tower_mass = Float(units='kg', iotype='in', desc='component mass [kg]')

    # Parameters
    blade_number = Int(3, iotype='in', desc = 'number of rotor blades')
    bearing_number = Int(2, iotype='in', desc = 'number of main bearings')

    # Outputs
    hub_system_mass = Float(units='kg', iotype='out', desc='hub system mass')
    rotor_mass = Float(units='kg', iotype='out', desc='hub system mass')
    nacelle_mass = Float(units='kg', iotype='out', desc='nacelle mass')
    turbine_mass = Float(units='kg', iotype='out', desc='turbine mass')
    
    def execute(self):
        
        self.hub_system_mass = self.hub_mass + self.pitch_system_mass + self.spinner_mass
        self.rotor_mass = self.blade_mass * self.blade_number + self.hub_system_mass
        self.nacelle_mass = self.low_speed_shaft_mass + self.bearing_number * self.main_bearing_mass + \
                            self.gearbox_mass + self.high_speed_side_mass + self.generator_mass + \
                            self.bedplate_mass + self.yaw_system_mass + self.hydraulic_cooling_mass + \
                            self.nacelle_cover_mass + self.other_mass + self.transformer_mass
        self.turbine_mass = self.rotor_mass + self.nacelle_mass + self.tower_mass

# --------------------------------------------------------------------

class nrel_csm_mass_2015(Assembly):

    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    turbine_class = Enum('I', ('I', 'II/III', 'User Exponent'), iotype = 'in', desc='turbine class')
    blade_has_carbon = Bool(False, iotype='in', desc= 'does the blade have carbon?') #default to doesn't have carbon
    blade_number = Int(iotype='in', desc='number of rotor blades')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    rotor_torque = Float(iotype='in', units='N * m', desc = 'torque from rotor at rated power') #JMF do we want this default?
    crane = Bool(False, iotype='in', desc='flag for presence of onboard crane')
    hub_height = Float(units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')
    bearing_number = Int(2, iotype='in', desc = 'number of main bearings')

    # Coefficients and Exponents
    blade_mass_coefficient = Float(0.5, iotype='in', desc= 'A in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    rotor_diameter_denominator = Float(2.0, iotype='in', desc= 'B in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    blade_user_exponent = Float(2.5, iotype='in', desc='optional user-entered exponent for the blade mass equation')
    
    hub_mass_coeff = Float(2.3, iotype='in', desc= 'A in the hub mass equation: A*blade_mass + B') #default from ppt
    hub_mass_intercept = Float(1320, iotype='in', desc= 'B in the hub mass equation: A*blade_mass + B') #default from ppt
    
    pitch_bearing_mass_coeff = Float(0.1295, iotype='in', desc='A in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    pitch_bearing_mass_intercept = Float(491.31, iotype='in', desc='B in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    bearing_housing_percent = Float(.3280, iotype='in', desc='bearing housing percentage (in decimal form: ex 10% is 0.10)') #default from old CSM
    mass_sys_offset = Float(555.0, iotype='in', desc='mass system offset') #default from old CSM
    
    spinner_mass_coeff = Float(15.5, iotype='in', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    spinner_mass_intercept = Float(-980.0, iotype='in', desc= 'B in the spinner mass equation: A*rotor_diameter + B')
    
    lss_mass_coeff = Float(13., iotype='in', desc='A in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_exp = Float(0.65, iotype='in', desc='exp in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_intercept = Float(775., iotype='in', desc='B in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    
    bearing_mass_coeff = Float(0.0001, iotype='in', desc= 'A in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
    bearing_mass_exp = Float(3.5, iotype='in', desc= 'exp in the bearing mass equation: A*rotor_diameter^exp') #default from ppt

    gearbox_mass_coeff = Float(113., iotype='in', desc= 'A in the gearbox mass equation: A*rotor_torque^exp')
    gearbox_mass_exp = Float(0.71, iotype='in', desc= 'exp in the gearbox mass equation: A*rotor_torque^exp')

    hss_mass_coeff = Float(0.19894, iotype='in', desc= 'NREL CSM hss equation; removing intercept since it is negligible')

    generator_mass_coeff = Float(2300., iotype='in', desc= 'A in the generator mass equation: A*rated_power + B') #default from ppt
    generator_mass_intercept = Float(3400., iotype='in', desc= 'B in the generator mass equation: A*rated_power + B') #default from ppt

    bedplate_mass_exp = Float(2.2, iotype='in', desc= 'exp in the bedplate mass equation: rotor_diameter^exp')

    yaw_mass_coeff = Float(0.00144, iotype='in', desc= 'A in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
    yaw_mass_exp = Float(3.314, iotype='in', desc= 'exp in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM

    hvac_mass_coeff = Float(0.08, iotype='in', desc= 'hvac linear coefficient') #NREL CSM

    cover_mass_coeff = Float(1.2819, iotype='in', units='USD/kW', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    cover_mass_intercept = Float(427.74, iotype='in', units='USD', desc= 'B in the spinner mass equation: A*rotor_diameter + B')

    nacelle_platforms_mass_coeff = Float(0.125, iotype='in', units='kg/kg', desc='nacelle platforms mass coefficient as a function of bedplate mass [kg/kg]') #default from old CSM
    crane_weight = Float(3000., iotype='in', units='kg', desc='weight of onboard crane')

    transformer_mass_coeff = Float(1915., iotype='in', desc= 'A in the transformer mass equation: A*rated_power + B') #default from ppt
    transformer_mass_intercept = Float(1910., iotype='in', desc= 'B in the transformer mass equation: A*rated_power + B') #default from ppt

    tower_mass_coeff = Float(19.828, iotype='in', desc= 'A in the tower mass equation: A*hub_height + B') #default from ppt
    tower_mass_exp = Float(2.0282, iotype='in', desc= 'B in the tower mass equation: A*hub_height + B') #default from ppt

    # Outputs
    blade_mass = Float(units='kg', iotype='out', desc= 'component mass [kg]')
    hub_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    pitch_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    spinner_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    low_speed_shaft_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    main_bearing_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    gearbox_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    high_speed_side_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    generator_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    bedplate_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    yaw_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    hydraulic_cooling_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    nacelle_cover_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    other_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    transformer_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    tower_mass = Float(units='kg', iotype='out', desc='component mass [kg]')

    hub_system_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    rotor_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    turbine_mass = Float(0.0, units='kg', iotype='out', desc='turbine mass')
    
    def configure(self):
        
        self.add('blade',BladeMass())
        self.add('hub',HubMass())
        self.add('pitch',PitchSystemMass())
        self.add('spinner',SpinnerMass())
        self.add('lss',LowSpeedShaftMass())
        self.add('bearing',BearingMass())
        self.add('gearbox',GearboxMass())
        self.add('hss',HighSpeedSideMass())
        self.add('generator',GeneratorMass())
        self.add('bedplate',BedplateMass())
        self.add('yaw',YawSystemMass())
        self.add('hvac',HydraulicCoolingMass())
        self.add('cover',NacelleCoverMass())
        self.add('other',OtherMainframeMass())
        self.add('transformer',TransformerMass())
        self.add('tower',TowerMass())
        self.add('turbine',turbine_mass_adder())
        
        self.driver.workflow.add(['blade','hub', 'pitch', 'spinner', 'lss', 'bearing', 'gearbox', 'hss', 'generator', \
                                  'bedplate', 'yaw', 'hvac', 'cover', 'other', 'transformer', 'tower', 'turbine'])
        
        # connect input
        self.connect('rotor_diameter',['blade.rotor_diameter','spinner.rotor_diameter','bearing.rotor_diameter', \
                                       'bedplate.rotor_diameter','yaw.rotor_diameter'])
        self.connect('turbine_class','blade.turbine_class')
        self.connect('blade_has_carbon','blade.blade_has_carbon')
        self.connect('blade_number',['pitch.blade_number','turbine.blade_number'])
        self.connect('machine_rating',['lss.machine_rating','hss.machine_rating', 'generator.machine_rating', \
                                       'hvac.machine_rating', 'cover.machine_rating', 'transformer.machine_rating'])
        self.connect('rotor_torque','gearbox.rotor_torque')
        self.connect('crane','other.crane')
        self.connect('hub_height','tower.hub_height')
        self.connect('bearing_number','turbine.bearing_number')

        #TODO: add connections for coefficients and variables

        # connect between components / outputs
        self.connect('blade.blade_mass',['blade_mass', 'hub.blade_mass','pitch.blade_mass','lss.blade_mass','turbine.blade_mass'])
        self.connect('hub.hub_mass',['hub_mass', 'turbine.hub_mass'])
        self.connect('pitch.pitch_system_mass',['pitch_system_mass', 'turbine.pitch_system_mass'])
        self.connect('spinner.spinner_mass', ['spinner_mass', 'turbine.spinner_mass'])
        self.connect('lss.low_speed_shaft_mass', ['low_speed_shaft_mass', 'turbine.low_speed_shaft_mass'])
        self.connect('bearing.main_bearing_mass',['main_bearing_mass', 'turbine.main_bearing_mass'])
        self.connect('gearbox.gearbox_mass',['gearbox_mass','turbine.gearbox_mass'])
        self.connect('hss.high_speed_side_mass',['high_speed_side_mass', 'turbine.high_speed_side_mass'])
        self.connect('generator.generator_mass',['generator_mass', 'turbine.generator_mass'])
        self.connect('bedplate.bedplate_mass',['bedplate_mass', 'other.bedplate_mass', 'turbine.bedplate_mass'])
        self.connect('yaw.yaw_system_mass',['yaw_system_mass', 'turbine.yaw_system_mass'])
        self.connect('hvac.hydraulic_cooling_mass',['hydraulic_cooling_mass', 'turbine.hydraulic_cooling_mass'])
        self.connect('cover.nacelle_cover_mass', ['nacelle_cover_mass', 'turbine.nacelle_cover_mass'])
        self.connect('other.other_mass',['other_mass', 'turbine.other_mass'])
        self.connect('transformer.transformer_mass', ['transformer_mass', 'turbine.transformer_mass'])
        self.connect('tower.tower_mass',['tower_mass', 'turbine.tower_mass'])
        self.connect('turbine.hub_system_mass','hub_system_mass')
        self.connect('turbine.rotor_mass','rotor_mass')
        self.connect('turbine.nacelle_mass','nacelle_mass')
        self.connect('turbine.turbine_mass','turbine_mass')

@implement_base(BaseTurbineCostModel)
class nrel_csm_tcc_2015(Assembly):

    # Variables
    rotor_diameter = Float(units = 'm', iotype='in', desc= 'rotor diameter of the machine')
    turbine_class = Enum('I', ('I', 'II/III', 'User Exponent'), iotype = 'in', desc='turbine class')
    blade_has_carbon = Bool(False, iotype='in', desc= 'does the blade have carbon?') #default to doesn't have carbon
    blade_number = Int(iotype='in', desc='number of rotor blades')
    machine_rating = Float(iotype='in', units='kW', desc='machine rating')
    rotor_torque = Float(iotype='in', units='N * m', desc = 'torque from rotor at rated power') #JMF do we want this default?
    crane = Bool(False, iotype='in', desc='flag for presence of onboard crane')
    hub_height = Float(units = 'm', iotype='in', desc= 'hub height of wind turbine above ground / sea level')
    bearing_number = Int(2, iotype='in', desc = 'number of main bearings')
    # Additional cost variables
    offshore = Bool(iotype='in', desc='flag for offshore project')

    # Coefficients and Exponents
    blade_mass_coefficient = Float(0.5, iotype='in', desc= 'A in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    rotor_diameter_denominator = Float(2.0, iotype='in', desc= 'B in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
    blade_user_exponent = Float(2.5, iotype='in', desc='optional user-entered exponent for the blade mass equation')
    
    hub_mass_coeff = Float(2.3, iotype='in', desc= 'A in the hub mass equation: A*blade_mass + B') #default from ppt
    hub_mass_intercept = Float(1320, iotype='in', desc= 'B in the hub mass equation: A*blade_mass + B') #default from ppt
    
    pitch_bearing_mass_coeff = Float(0.1295, iotype='in', desc='A in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    pitch_bearing_mass_intercept = Float(491.31, iotype='in', desc='B in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
    bearing_housing_percent = Float(.3280, iotype='in', desc='bearing housing percentage (in decimal form: ex 10% is 0.10)') #default from old CSM
    mass_sys_offset = Float(555.0, iotype='in', desc='mass system offset') #default from old CSM
    
    spinner_mass_coeff = Float(15.5, iotype='in', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    spinner_mass_intercept = Float(-980.0, iotype='in', desc= 'B in the spinner mass equation: A*rotor_diameter + B')
    
    lss_mass_coeff = Float(13., iotype='in', desc='A in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_exp = Float(0.65, iotype='in', desc='exp in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    lss_mass_intercept = Float(775., iotype='in', desc='B in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
    
    bearing_mass_coeff = Float(0.0001, iotype='in', desc= 'A in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
    bearing_mass_exp = Float(3.5, iotype='in', desc= 'exp in the bearing mass equation: A*rotor_diameter^exp') #default from ppt

    gearbox_mass_coeff = Float(113., iotype='in', desc= 'A in the gearbox mass equation: A*rotor_torque^exp')
    gearbox_mass_exp = Float(0.71, iotype='in', desc= 'exp in the gearbox mass equation: A*rotor_torque^exp')

    hss_mass_coeff = Float(0.19894, iotype='in', desc= 'NREL CSM hss equation; removing intercept since it is negligible')

    generator_mass_coeff = Float(2300., iotype='in', desc= 'A in the generator mass equation: A*rated_power + B') #default from ppt
    generator_mass_intercept = Float(3400., iotype='in', desc= 'B in the generator mass equation: A*rated_power + B') #default from ppt

    bedplate_mass_exp = Float(2.2, iotype='in', desc= 'exp in the bedplate mass equation: rotor_diameter^exp')

    yaw_mass_coeff = Float(0.00144, iotype='in', desc= 'A in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
    yaw_mass_exp = Float(3.314, iotype='in', desc= 'exp in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM

    hvac_mass_coeff = Float(0.08, iotype='in', desc= 'hvac linear coefficient') #NREL CSM

    cover_mass_coeff = Float(1.2819, iotype='in', units='USD/kW', desc= 'A in the spinner mass equation: A*rotor_diameter + B')
    cover_mass_intercept = Float(427.74, iotype='in', units='USD', desc= 'B in the spinner mass equation: A*rotor_diameter + B')

    nacelle_platforms_mass_coeff = Float(0.125, iotype='in', units='kg/kg', desc='nacelle platforms mass coefficient as a function of bedplate mass [kg/kg]') #default from old CSM
    crane_weight = Float(3000., iotype='in', units='kg', desc='weight of onboard crane')

    transformer_mass_coeff = Float(1915., iotype='in', desc= 'A in the transformer mass equation: A*rated_power + B') #default from ppt
    transformer_mass_intercept = Float(1910., iotype='in', desc= 'B in the transformer mass equation: A*rated_power + B') #default from ppt

    tower_mass_coeff = Float(19.828, iotype='in', desc= 'A in the tower mass equation: A*hub_height + B') #default from ppt
    tower_mass_exp = Float(2.0282, iotype='in', desc= 'B in the tower mass equation: A*hub_height + B') #default from ppt

    # cost coefficients
    blade_mass_cost_coeff = Float(13.08, iotype='in', units='USD/kg', desc='blade mass-cost coefficient [$/kg]')
    hub_mass_cost_coeff = Float(3.80, iotype='in', units='USD/kg', desc='hub mass-cost coefficient [$/kg]')
    pitch_system_mass_cost_coeff = Float(22.91, iotype='in', units='USD/kg', desc='pitch system mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    spinner_mass_cost_coeff = Float(23.00, iotype='in', units='USD/kg', desc='spinner/nose cone mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    lss_mass_cost_coeff = Float(12.60, iotype='in', units='USD/kg', desc='low speed shaft mass-cost coefficient [$/kg]')
    bearings_mass_cost_coeff = Float(6.35, iotype='in', units='USD/kg', desc='main bearings mass-cost coefficient [$/kg]') #mass-cost coefficient- HALF of the 12.70 in powerpoint because it was based on TWO bearings 
    gearbox_mass_cost_coeff = Float(17.40, iotype='in', units='USD/kg', desc='gearbox mass-cost coefficient [$/kg]')
    high_speed_side_mass_cost_coeff = Float(8.25, iotype='in', units='USD/kg', desc='high speed side mass-cost coefficient [$/kg]') #mass-cost coefficient with default from list
    generator_mass_cost_coeff = Float(17.43, iotype='in', units= 'USD/kg', desc='generator mass cost coefficient [$/kg]')
    bedplate_mass_cost_coeff = Float(4.50, iotype='in', units='USD/kg', desc='bedplate mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    yaw_system_mass_cost_coeff = Float(11.01, iotype='in', units='USD/kg', desc='yaw system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    variable_speed_elec_mass_cost_coeff = Float(26.50, iotype='in', units='USD/kg', desc='variable speed electronics mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    hydraulic_cooling_mass_cost_coeff = Float(163.95, iotype='in', units='USD/kg', desc='hydraulic and cooling system mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    nacelle_cover_mass_cost_coeff = Float(7.61, iotype='in', units='USD/kg', desc='nacelle cover mass cost coefficient [$/kg]') #mass-cost coefficient with default from list
    elec_connec_cost_esc = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for electrical connections') ####KLD update this
    elec_connec_machine_rating_cost_coeff = Float(40.0, iotype='in', units='USD/kW', desc='2002 electrical connections cost coefficient per kW')
    controls_cost_base = Array(np.array([35000.0,55900.0]), iotype='in', desc='2002 controls cost for [onshore, offshore]')
    controls_escalator = Float(1.5, iotype='in', desc='cost escalator from 2002 to 2015 for controls') ####KLD update this
    nacelle_platforms_mass_cost_coeff = Float(8.7, iotype='in', units='USD/kg', desc='nacelle platforms mass cost coefficient [$/kg]') #default from old CSM
    crane_cost = Float(12000.0, iotype='in', units='USD', desc='crane cost if present [$]') #default from old CSM
    base_hardware_cost_coeff = Float(0.7, iotype='in', desc='base hardware cost coefficient based on bedplate cost') #default from old CSM
    transformer_mass_cost_coeff = Float(26.5, iotype='in', units= 'USD/kg', desc='transformer mass cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
    tower_mass_cost_coefficient = Float(3.20, iotype='in', units='USD/kg', desc='tower mass-cost coefficient [$/kg]') #mass-cost coefficient with default from ppt
  
    #cost assembly multipliers
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
    blade_mass = Float(units='kg', iotype='out', desc= 'component mass [kg]')
    hub_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    pitch_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    spinner_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    low_speed_shaft_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    main_bearing_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    gearbox_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    high_speed_side_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    generator_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    bedplate_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    yaw_system_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    hydraulic_cooling_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    nacelle_cover_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    other_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    transformer_mass = Float(units='kg', iotype='out', desc='component mass [kg]')
    tower_mass = Float(units='kg', iotype='out', desc='component mass [kg]')

    hub_system_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    rotor_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    nacelle_mass = Float(0.0, units='kg', iotype='out', desc='nacelle mass')
    turbine_mass = Float(0.0, units='kg', iotype='out', desc='turbine mass')

    # Outputs
    turbine_cost = Float(0.0, iotype='out', desc='Overall wind turbine capial costs including transportation costs')
    
    def configure(self):
        
        self.add('trb_mass',nrel_csm_mass_2015())
        self.add('tcc', Turbine_CostsSE_2015())
        
        self.driver.workflow.add(['tcc','trb_mass'])
        
        # connect input
        self.connect('rotor_diameter','trb_mass.rotor_diameter')
        self.connect('turbine_class','trb_mass.turbine_class')
        self.connect('blade_has_carbon','trb_mass.blade_has_carbon')
        self.connect('blade_number',['trb_mass.blade_number','tcc.blade_number'])
        self.connect('machine_rating',['trb_mass.machine_rating','tcc.machine_rating'])
        self.connect('rotor_torque','trb_mass.rotor_torque')
        self.connect('crane',['trb_mass.crane','tcc.crane'])
        self.connect('hub_height','trb_mass.hub_height')
        self.connect('bearing_number',['trb_mass.bearing_number','tcc.bearing_number'])
        self.connect('offshore','tcc.offshore')

        #TODO: add connections for coefficients and variables

        # connect between components / outputs
        self.connect('trb_mass.blade_mass',['blade_mass', 'tcc.blade_mass'])
        self.connect('trb_mass.hub_mass',['hub_mass', 'tcc.hub_mass'])
        self.connect('trb_mass.pitch_system_mass',['pitch_system_mass', 'tcc.pitch_system_mass'])
        self.connect('trb_mass.spinner_mass', ['spinner_mass', 'tcc.spinner_mass'])
        self.connect('trb_mass.low_speed_shaft_mass', ['low_speed_shaft_mass', 'tcc.low_speed_shaft_mass'])
        self.connect('trb_mass.main_bearing_mass',['main_bearing_mass', 'tcc.main_bearing_mass'])
        self.connect('trb_mass.gearbox_mass',['gearbox_mass','tcc.gearbox_mass'])
        self.connect('trb_mass.high_speed_side_mass',['high_speed_side_mass', 'tcc.high_speed_side_mass'])
        self.connect('trb_mass.generator_mass',['generator_mass', 'tcc.generator_mass'])
        self.connect('trb_mass.bedplate_mass',['bedplate_mass', 'tcc.bedplate_mass'])
        self.connect('trb_mass.yaw_system_mass',['yaw_system_mass', 'tcc.yaw_system_mass'])
        self.connect('trb_mass.hydraulic_cooling_mass',['hydraulic_cooling_mass', 'tcc.hydraulic_cooling_mass'])
        self.connect('trb_mass.nacelle_cover_mass', ['nacelle_cover_mass', 'tcc.nacelle_cover_mass'])
        # TODO: variable speed electronics and other mainframe costs
        self.connect('trb_mass.other_mass',['other_mass'])
        self.connect('trb_mass.transformer_mass', ['transformer_mass', 'tcc.transformer_mass'])
        self.connect('trb_mass.tower_mass',['tower_mass', 'tcc.tower_mass'])
        # outputs
        self.connect('trb_mass.hub_system_mass','hub_system_mass')
        self.connect('trb_mass.rotor_mass','rotor_mass')
        self.connect('trb_mass.nacelle_mass','nacelle_mass')
        self.connect('trb_mass.turbine_mass','turbine_mass')
        self.connect('tcc.turbine_cost','turbine_cost')


#-----------------------------------------------------------------

def mass_example():

    # simple test of module
    trb = nrel_csm_mass_2015()
    trb.rotor_diameter = 126.0
    trb.turbine_class = 'I'
    trb.blade_has_carbon = False
    trb.blade_number = 3    
    trb.machine_rating = 5000.0
    trb.hub_height = 90.0
    trb.bearing_number = 2
    trb.crane = True

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90

    ratedHubPower  = trb.machine_rating*1000. / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*trb.rotor_diameter)) * (60.0 / (2*np.pi))
    trb.rotor_torque = ratedHubPower/(rotorSpeed*(np.pi/30))

    print rotorSpeed
    print trb.rotor_torque

    trb.run()
    
    print "The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:"
    print "Overall turbine mass is {0:.2f} kg".format(trb.turbine_mass)
    for io in trb.list_outputs():
        val = getattr(trb, io)
        print io + ' ' + str(val)
    #print "Overall turbine cost is ${0:.2f} USD".format(trb.turbine_cost)

def cost_example():

    # simple test of module
    trb = nrel_csm_tcc_2015()
    trb.rotor_diameter = 126.0
    trb.turbine_class = 'I'
    trb.blade_has_carbon = False
    trb.blade_number = 3    
    trb.machine_rating = 5000.0
    trb.hub_height = 90.0
    trb.bearing_number = 2
    trb.crane = True
    trb.offshore = False

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90

    ratedHubPower  = trb.machine_rating*1000. / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*trb.rotor_diameter)) * (60.0 / (2*np.pi))
    trb.rotor_torque = ratedHubPower/(rotorSpeed*(np.pi/30))

    print rotorSpeed
    print trb.rotor_torque

    trb.run()
    
    print "The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:"
    print "Overall turbine mass is {0:.2f} kg".format(trb.turbine_mass)
    print "Overall turbine cost is ${0:.2f} USD".format(trb.turbine_cost)

    for io in trb.list_outputs():
        val = getattr(trb, io)
        print io + ' ' + str(val)

if __name__ == "__main__":

    mass_example()
    
    cost_example()