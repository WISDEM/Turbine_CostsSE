"""
tcc_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import numpy as np

from openmdao.api import Component, Problem, Group, IndepVarComp

from turbine_costsse.turbine_costsse_2015 import Turbine_CostsSE_2015

# --------------------------------------------------------------------
class BladeMass(Component):
    
    def __init__(self):
        super(BladeMass, self).__init__()
        
        # Variables
        self.add_param('rotor_diameter', 0.0, desc= 'rotor diameter of the machine')
        self.add_param('turbine_class', 1, desc='turbine class')
        self.add_param('blade_has_carbon', False, desc= 'does the blade have carbon?') #default to doesn't have carbon
        self.add_param('blade_mass_coeff', 0.5, desc= 'A in the blade mass equation: A*(rotor_diameter/B)^exp') #default from ppt
        self.add_param('blade_user_exp', 2.5, desc='optional user-entered exp for the blade mass equation')
        
        # Outputs
        self.add_output('blade_mass', 0.0, desc= 'component mass [kg]')
  
    def solve_nonlinear(self, params, unknowns, resids):

        rotor_diameter = params['rotor_diameter']
        turbine_class = params['turbine_class']
        blade_has_carbon = params['blade_has_carbon']
        blade_mass_coeff = params['blade_mass_coeff']
        blade_user_exp = params['blade_user_exp']
    
        # select the exp for the blade mass equation
        exp = 0.0
        if turbine_class == 1:
            if blade_has_carbon:
              exp = 2.47
            else:
              exp = 2.54
        elif turbine_class > 1:
            if blade_has_carbon:
              exp = 2.44
            else:
              exp = 2.50
        else:
            exp = blade_user_exp
        
        # calculate the blade mass
        unknowns['blade_mass'] = blade_mass_coeff * (rotor_diameter / 2)**exp

  # --------------------------------------------------------------------
class HubMass(Component):

    def __init__(self):
        super(HubMass, self).__init__()
        
        # Variables
        self.add_param('blade_mass', 0.0, desc= 'component mass [kg]')
        self.add_param('hub_mass_coeff', 2.3, desc= 'A in the hub mass equation: A*blade_mass + B') #default from ppt
        self.add_param('hub_mass_intercept', 1320., desc= 'B in the hub mass equation: A*blade_mass + B') #default from ppt
        
        # Outputs
        self.add_output('hub_mass', 0.0, desc='component mass [kg]')
  
    def solve_nonlinear(self, params, unknowns, resids):
      
        blade_mass = params['blade_mass']
        hub_mass_coeff = params['hub_mass_coeff']
        hub_mass_intercept = params['hub_mass_intercept']
        
        # calculate the hub mass
        unknowns['hub_mass'] = hub_mass_coeff * blade_mass + hub_mass_intercept

# --------------------------------------------------------------------
class PitchSystemMass(Component):
    
    def __init__(self):
        super(PitchSystemMass, self).__init__()
        
        self.add_param('blade_mass', 0.0, desc= 'component mass [kg]')
        self.add_param('blade_number', 3, desc='number of rotor blades')
        self.add_param('pitch_bearing_mass_coeff', 0.1295, desc='A in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
        self.add_param('pitch_bearing_mass_intercept', 491.31, desc='B in the pitch bearing mass equation: A*blade_mass*blade_number + B') #default from old CSM
        self.add_param('bearing_housing_percent', .3280, desc='bearing housing percentage (in decimal form: ex 10% is 0.10)') #default from old CSM
        self.add_param('mass_sys_offset', 555.0, desc='mass system offset') #default from old CSM
        
        # Outputs
        self.add_output('pitch_system_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        blade_mass = params['blade_mass']
        blade_number = params['blade_number']
        pitch_bearing_mass_coeff = params['pitch_bearing_mass_coeff']
        pitch_bearing_mass_intercept = params['pitch_bearing_mass_intercept']
        bearing_housing_percent = params['bearing_housing_percent']
        mass_sys_offset = params['mass_sys_offset']
        
        # calculate the hub mass
        pitchBearingMass = pitch_bearing_mass_coeff * blade_mass * blade_number + pitch_bearing_mass_intercept
        unknowns['pitch_system_mass'] = pitchBearingMass * (1 + bearing_housing_percent) + mass_sys_offset

# --------------------------------------------------------------------
class SpinnerMass(Component):

    def __init__(self):
        
        super(SpinnerMass, self).__init__()
    
        # Variables
        self.add_param('rotor_diameter', 0.0, desc= 'rotor diameter of the machine')
        self.add_param('spinner_mass_coeff', 15.5, desc= 'A in the spinner mass equation: A*rotor_diameter + B')
        self.add_param('spinner_mass_intercept', -980.0, desc= 'B in the spinner mass equation: A*rotor_diameter + B')
        
        # Outputs
        self.add_output('spinner_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        rotor_diameter = params['rotor_diameter']
        spinner_mass_coeff = params['spinner_mass_coeff']
        spinner_mass_intercept = params['spinner_mass_intercept']
        
        # calculate the spinner mass
        unknowns['spinner_mass'] = spinner_mass_coeff * rotor_diameter + spinner_mass_intercept

# --------------------------------------------------------------------
class LowSpeedShaftMass(Component):

    def __init__(self):
        
        super(LowSpeedShaftMass, self).__init__()
        
        # Variables
        self.add_param('blade_mass', 0.0, desc='mass for a single wind turbine blade')
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('lss_mass_coeff', 13., desc='A in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
        self.add_param('lss_mass_exp', 0.65, desc='exp in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
        self.add_param('lss_mass_intercept', 775., desc='B in the lss mass equation: A*(blade_mass*rated_power)^exp + B')
        
        # Outputs
        self.add_output('lss_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        blade_mass = params['blade_mass']
        machine_rating = params['machine_rating']
        lss_mass_coeff = params['lss_mass_coeff']
        lss_mass_exp = params['lss_mass_exp']
        lss_mass_intercept = params['lss_mass_intercept']
    
        # calculate the lss mass
        unknowns['lss_mass'] = lss_mass_coeff * (blade_mass * machine_rating/1000.)**lss_mass_exp + lss_mass_intercept

# --------------------------------------------------------------------
class BearingMass(Component):

    def __init__(self):

        super(BearingMass, self).__init__()

        # Variables
        self.add_param('rotor_diameter', 0.0, desc= 'rotor diameter of the machine')
        self.add_param('bearing_mass_coeff', 0.0001, desc= 'A in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
        self.add_param('bearing_mass_exp', 3.5, desc= 'exp in the bearing mass equation: A*rotor_diameter^exp') #default from ppt
        
        # Outputs
        self.add_output('main_bearing_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        rotor_diameter = params['rotor_diameter']
        bearing_mass_coeff = params['bearing_mass_coeff']
        bearing_mass_exp = params['bearing_mass_exp']
        
        # calculates the mass of a SINGLE bearing
        unknowns['main_bearing_mass'] = bearing_mass_coeff * rotor_diameter ** bearing_mass_exp

# --------------------------------------------------------------------
class GearboxMass(Component):

    def __init__(self):
  
        super(GearboxMass, self).__init__()
  
        # Variables
        self.add_param('rotor_torque', 0.0, desc = 'torque from rotor at rated power') #JMF do we want this default?
        self.add_param('gearbox_mass_coeff', 113., desc= 'A in the gearbox mass equation: A*rotor_torque^exp')
        self.add_param('gearbox_mass_exp', 0.71, desc= 'exp in the gearbox mass equation: A*rotor_torque^exp')
        
        # Outputs
        self.add_output('gearbox_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        rotor_torque = params['rotor_torque']
        gearbox_mass_coeff = params['gearbox_mass_coeff']
        gearbox_mass_exp = params['gearbox_mass_exp']
        
        # calculate the gearbox mass
        unknowns['gearbox_mass'] = gearbox_mass_coeff * (rotor_torque/1000.0)**gearbox_mass_exp

# --------------------------------------------------------------------
class HighSpeedSideMass(Component):

    def __init__(self):
      
        super(HighSpeedSideMass, self).__init__()

        # Variables
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('hss_mass_coeff', 0.19894, desc= 'NREL CSM hss equation; removing intercept since it is negligible')
        
        # Outputs
        self.add_output('hss_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        machine_rating = params['machine_rating']
        hss_mass_coeff = params['hss_mass_coeff']
        
        # TODO: this is in DriveSE; replace this with code in DriveSE and have DriveSE use this code??
        unknowns['hss_mass'] = hss_mass_coeff * machine_rating

# --------------------------------------------------------------------
class GeneratorMass(Component):

    def __init__(self):
      
        
        super(GeneratorMass, self).__init__()
  
        # Variables
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('generator_mass_coeff', 2300., desc= 'A in the generator mass equation: A*rated_power + B') #default from ppt
        self.add_param('generator_mass_intercept', 3400., desc= 'B in the generator mass equation: A*rated_power + B') #default from ppt
        
        # Outputs
        self.add_output('generator_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):

        machine_rating = params['machine_rating']
        generator_mass_coeff = params['generator_mass_coeff']
        generator_mass_intercept = params['generator_mass_intercept']
    
        # calculate the generator mass
        unknowns['generator_mass'] = generator_mass_coeff * machine_rating/1000. + generator_mass_intercept

# --------------------------------------------------------------------
class BedplateMass(Component):

    def __init__(self):

        super(BedplateMass, self).__init__()

        # Variables
        self.add_param('rotor_diameter', 0.0, desc= 'rotor diameter of the machine')
        self.add_param('bedplate_mass_exp', 2.2, desc= 'exp in the bedplate mass equation: rotor_diameter^exp')
        
        # Outputs
        self.add_output('bedplate_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        rotor_diameter = params['rotor_diameter']
        bedplate_mass_exp = params['bedplate_mass_exp']
        
        # calculate the bedplate mass
        unknowns['bedplate_mass'] = rotor_diameter**bedplate_mass_exp

# --------------------------------------------------------------------
class YawSystemMass(Component):
  
    def __init__(self):

        super(YawSystemMass, self).__init__()

        # Variables
        self.add_param('rotor_diameter', 0.0, desc= 'rotor diameter of the machine')
        self.add_param('yaw_mass_coeff', 0.0009, desc= 'A in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
        self.add_param('yaw_mass_exp', 3.314, desc= 'exp in the yaw mass equation: A*rotor_diameter^exp') #NREL CSM
        
        # Outputs
        self.add_output('yaw_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
      
        rotor_diameter = params['rotor_diameter']
        yaw_mass_coeff = params['yaw_mass_coeff']
        yaw_mass_exp = params['yaw_mass_exp']
    
        # calculate yaw system mass #TODO - 50% adder for non-bearing mass
        unknowns['yaw_mass'] = 1.5 * (yaw_mass_coeff * rotor_diameter ** yaw_mass_exp) #JMF do we really want to expose all these?

#TODO: no variable speed mass; ignore for now

# --------------------------------------------------------------------
class HydraulicCoolingMass(Component):
    
    def __init__(self):
    
        super(HydraulicCoolingMass, self).__init__()
        
        # Variables
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('hvac_mass_coeff', 0.08, desc= 'hvac linear coeff') #NREL CSM
        
        # Outputs
        self.add_output('hvac_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        machine_rating = params['machine_rating']
        hvac_mass_coeff = params['hvac_mass_coeff']
        
        # calculate hvac system mass
        unknowns['hvac_mass'] = hvac_mass_coeff * machine_rating

# --------------------------------------------------------------------
class NacelleCoverMass(Component):

    def __init__(self):
    
        super(NacelleCoverMass, self).__init__()
    
        # Variables
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('cover_mass_coeff', 1.2817, desc= 'A in the spinner mass equation: A*rotor_diameter + B')
        self.add_param('cover_mass_intercept', 428.19, desc= 'B in the spinner mass equation: A*rotor_diameter + B')
        
        # Outputs
        self.add_output('cover_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        machine_rating = params['machine_rating']
        cover_mass_coeff = params['cover_mass_coeff']
        cover_mass_intercept = params['cover_mass_intercept']
        
        # calculate nacelle cover mass
        unknowns['cover_mass'] = cover_mass_coeff * machine_rating + cover_mass_intercept

# TODO: ignoring controls and electronics mass for now

# --------------------------------------------------------------------
class OtherMainframeMass(Component):
    # nacelle platforms, service crane, base hardware
    
    def __init__(self):
    
        super(OtherMainframeMass, self).__init__()
        
        # Variables
        self.add_param('bedplate_mass', 0.0, desc='component mass [kg]')
        self.add_param('platforms_mass_coeff', 0.125, desc='nacelle platforms mass coeff as a function of bedplate mass [kg/kg]') #default from old CSM
        self.add_param('crane', False, desc='flag for presence of onboard crane')
        self.add_param('crane_weight', 3000., desc='weight of onboard crane')
        #TODO: there is no base hardware mass model in the old model. Cost is not dependent on mass.
        
        # Outputs
        self.add_output('other_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        bedplate_mass = params['bedplate_mass']
        platforms_mass_coeff = params['platforms_mass_coeff']
        crane = params['crane']
        crane_weight = params['crane_weight']
        
        # calculate nacelle cover mass           
        platforms_mass = platforms_mass_coeff * bedplate_mass

        # --- crane ---        
        if (crane):
            crane_mass =  crane_weight
        else:
            crane_mass = 0.  
        
        unknowns['other_mass'] = platforms_mass + crane_mass

# --------------------------------------------------------------------
class TransformerMass(Component):

    def __init__(self):
    
        super(TransformerMass, self).__init__()
    
        # Variables
        self.add_param('machine_rating', 0.0, desc='machine rating')
        self.add_param('transformer_mass_coeff', 1915., desc= 'A in the transformer mass equation: A*rated_power + B') #default from ppt
        self.add_param('transformer_mass_intercept', 1910., desc= 'B in the transformer mass equation: A*rated_power + B') #default from ppt
        
        # Outputs
        self.add_output('transformer_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        machine_rating = params['machine_rating']
        transformer_mass_coeff = params['transformer_mass_coeff']
        transformer_mass_intercept = params['transformer_mass_intercept']
        
        # calculate the transformer mass
        unknowns['transformer_mass'] = transformer_mass_coeff * machine_rating/1000. + transformer_mass_intercept

# --------------------------------------------------------------------
class TowerMass(Component):
  
    def __init__(self):

        super(TowerMass, self).__init__()

        # Variables
        self.add_param('hub_height', 0.0, desc= 'hub height of wind turbine above ground / sea level')
        self.add_param('tower_mass_coeff', 19.828, desc= 'A in the tower mass equation: A*hub_height^B') #default from ppt
        self.add_param('tower_mass_exp', 2.0282, desc= 'B in the tower mass equation: A*hub_height^B') #default from ppt
        
        # Outputs
        self.add_output('tower_mass', 0.0, desc='component mass [kg]')
    
    def solve_nonlinear(self, params, unknowns, resids):
        
        hub_height = params['hub_height']
        tower_mass_coeff = params['tower_mass_coeff']
        tower_mass_exp = params['tower_mass_exp']
        
        # calculate the tower mass
        unknowns['tower_mass'] = tower_mass_coeff * hub_height ** tower_mass_exp
 

# Turbine mass adder
class turbine_mass_adder(Component):
    
    def __init__(self):
        
        super(turbine_mass_adder, self).__init__()
    
        # Inputs
        # rotor
        self.add_param('blade_mass', 0.0, desc= 'component mass [kg]')
        self.add_param('hub_mass', 0.0, desc='component mass [kg]')
        self.add_param('pitch_system_mass', 0.0, desc='component mass [kg]')
        self.add_param('spinner_mass', 0.0, desc='component mass [kg]')
        # nacelle
        self.add_param('lss_mass', 0.0, desc='component mass [kg]')
        self.add_param('main_bearing_mass', 0.0, desc='component mass [kg]')
        self.add_param('gearbox_mass', 0.0, desc='component mass [kg]')
        self.add_param('hss_mass', 0.0, desc='component mass [kg]')
        self.add_param('generator_mass', 0.0, desc='component mass [kg]')
        self.add_param('bedplate_mass', 0.0, desc='component mass [kg]')
        self.add_param('yaw_mass', 0.0, desc='component mass [kg]')
        self.add_param('hvac_mass', 0.0, desc='component mass [kg]')
        self.add_param('cover_mass', 0.0, desc='component mass [kg]')
        self.add_param('other_mass', 0.0, desc='component mass [kg]')
        self.add_param('transformer_mass', 0.0, desc='component mass [kg]')
        # tower
        self.add_param('tower_mass', 0.0, desc='component mass [kg]')
    
        # Parameters
        self.add_param('blade_number', 3, desc = 'number of rotor blades')
        self.add_param('bearing_number', 2, desc = 'number of main bearings')
    
        # Outputs
        self.add_output('hub_system_mass', 0.0, desc='hub system mass')
        self.add_output('rotor_mass', 0.0, desc='hub system mass')
        self.add_output('nacelle_mass', 0.0, desc='nacelle mass')
        self.add_output('turbine_mass', 0.0, desc='turbine mass')
    
    def solve_nonlinear(self, params, unknowns, resids):

        blade_mass = params['blade_mass']
        hub_mass = params['hub_mass']
        pitch_system_mass = params['pitch_system_mass']
        spinner_mass = params['spinner_mass']
        lss_mass = params['lss_mass']
        main_bearing_mass = params['main_bearing_mass']
        gearbox_mass = params['gearbox_mass']
        hss_mass = params['hss_mass']
        generator_mass = params['generator_mass']
        bedplate_mass = params['bedplate_mass']
        yaw_mass = params['yaw_mass']
        hvac_mass = params['hvac_mass']
        cover_mass = params['cover_mass']
        other_mass = params['other_mass']
        transformer_mass = params['transformer_mass']
        tower_mass = params['tower_mass']
        blade_number = params['blade_number']
        bearing_number = params['bearing_number']
        
        
        unknowns['hub_system_mass'] = hub_mass + pitch_system_mass + spinner_mass
        unknowns['rotor_mass'] = blade_mass * blade_number + unknowns['hub_system_mass']
        unknowns['nacelle_mass'] = lss_mass + bearing_number * main_bearing_mass + \
                            gearbox_mass + hss_mass + generator_mass + \
                            bedplate_mass + yaw_mass + hvac_mass + \
                            cover_mass + other_mass + transformer_mass
        unknowns['turbine_mass'] = unknowns['rotor_mass'] + unknowns['nacelle_mass'] + tower_mass

# --------------------------------------------------------------------

class nrel_csm_mass_2015(Group):
    
    def __init__(self):
      
        super(nrel_csm_mass_2015, self).__init__()

        self.add('blade',BladeMass(), promotes=['*'])
        self.add('hub',HubMass(), promotes=['*'])
        self.add('pitch',PitchSystemMass(), promotes=['*'])
        self.add('spinner',SpinnerMass(), promotes=['*'])
        self.add('lss',LowSpeedShaftMass(), promotes=['*'])
        self.add('bearing',BearingMass(), promotes=['*'])
        self.add('gearbox',GearboxMass(), promotes=['*'])
        self.add('hss',HighSpeedSideMass(), promotes=['*'])
        self.add('generator',GeneratorMass(), promotes=['*'])
        self.add('bedplate',BedplateMass(), promotes=['*'])
        self.add('yaw',YawSystemMass(), promotes=['*'])
        self.add('hvac',HydraulicCoolingMass(), promotes=['*'])
        self.add('cover',NacelleCoverMass(), promotes=['*'])
        self.add('other',OtherMainframeMass(), promotes=['*'])
        self.add('transformer',TransformerMass(), promotes=['*'])
        self.add('tower',TowerMass(), promotes=['*'])
        self.add('turbine',turbine_mass_adder(), promotes=['*'])
       

class nrel_csm_2015(Group):
	  
	  def __init__(self):
	  	  
	  	  super(nrel_csm_2015, self).__init__()
	  	  
	  	  self.add('desvars', IndepVarComp([('rotor_diameter', 0.0),
			    																 ('machine_rating', 0.0),							    																 
			    																 ]),promotes=['*'])
	  	  
	  	  self.add('nrel_csm_mass', nrel_csm_mass_2015(), promotes=['*'])
	  	  self.add('turbine_costs', Turbine_CostsSE_2015(), promotes=['*'])
	  	  

#-----------------------------------------------------------------

def mass_example():

    # simple test of module
    trb = nrel_csm_mass_2015()
    prob = Problem(trb)
    prob.setup()

    prob['rotor_diameter'] = 126.0
    prob['turbine_class'] = 1
    prob['blade_has_carbon'] = False
    prob['blade_number'] = 3    
    prob['machine_rating'] = 5000.0
    prob['hub_height'] = 90.0
    prob['bearing_number'] = 2
    prob['crane'] = True

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90

    ratedHubPower  = prob['machine_rating']*1000. / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*prob['rotor_diameter'])) * (60.0 / (2*np.pi))
    prob['rotor_torque'] = ratedHubPower/(rotorSpeed*(np.pi/30))

    prob.run()
   
    print("The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:")
    #print "Overall turbine mass is {0:.2f} kg".format(trb.turbine.params['turbine_mass'])
    for io in trb.unknowns:
        print(io + ' ' + str(trb.unknowns[io]))

def cost_example():

    # simple test of module
    trb = nrel_csm_2015()
    prob = Problem(trb)
    prob.setup()

    # simple test of module
    prob['rotor_diameter'] = 126.0
    prob['turbine_class'] = 1
    prob['blade_has_carbon'] = False
    prob['blade_number'] = 3    
    prob['machine_rating'] = 5000.0
    prob['hub_height'] = 90.0
    prob['bearing_number'] = 2
    prob['crane'] = True

    # Rotor force calculations for nacelle inputs
    maxTipSpd = 80.0
    maxEfficiency = 0.90

    ratedHubPower  = prob['machine_rating']*1000. / maxEfficiency 
    rotorSpeed     = (maxTipSpd/(0.5*prob['rotor_diameter'])) * (60.0 / (2*np.pi))
    prob['rotor_torque'] = ratedHubPower/(rotorSpeed*(np.pi/30))

    prob.run()

    print("The results for the NREL 5 MW Reference Turbine in an offshore 20 m water depth location are:")
    for io in trb.unknowns:
        print(io + ' ' + str(trb.unknowns[io]))

if __name__ == "__main__":

    mass_example()
    
    cost_example()
