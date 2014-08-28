"""
hub_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from commonse.config import *
import numpy as np

class hub_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    blade_mass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    blade_number = Int(3, iotype='in', desc= 'number of rotor blades')

    # Outputs
    hub_system_cost = Float(0.0, units='USD', iotype='out', desc='hub system cost')
    hub_system_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    hub_cost = Float(0.0, units='USD', iotype='out', desc='hub cost')
    hub_mass = Float(0.0, units='kg', iotype='out', desc='hub mass')
    pitch_system_cost = Float(0.0, units='USD', iotype='out', desc='pitch system cost')
    pitch_system_mass = Float(0.0, units='kg', iotype='out', desc='pitch system mass')
    spinner_cost = Float(0.0, units='USD', iotype='out', desc='spinner / nose cone cost')
    spinner_mass = Float(0.0, units='kg', iotype='out', desc='spinner / nose cone mass')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL _cost and Scaling Model (csmHub.py)  
        """

        super(hub_csm_component, self).__init__()

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes hub model of the NREL _cost and Scaling model to compute hub system component masses and costs.
        """
        print "In {0}.execute()...".format(self.__class__)

        #*** Pitch bearing and mechanism
        pitchBearingMass = 0.1295 * self.blade_mass*self.blade_number + 491.31  # slope*BldMass3 + int
        bearingHousingPct = 32.80 / 100.0
        massSysOffset = 555.0
        self.pitch_system_mass = pitchBearingMass * (1+bearingHousingPct) + massSysOffset
    
        #*** Hub
        self.hub_mass = 0.95402537 * self.blade_mass + 5680.272238
    
        #*** NoseCone/Spinner
        self.spinner_mass = 18.5*self.rotor_diameter +(-520.5)   # GNS

        self.hub_system_mass = self.hub_mass + self.pitch_system_mass + self.spinner_mass

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        #*** Pitch bearing and mechanism    
        bearingCost = (0.2106*self.rotor_diameter**2.6576)
        bearingCostEscalator = ppi.compute('IPPI_PMB')
        self.pitch_system_cost = bearingCostEscalator * ( bearingCost + bearingCost * 1.28 )
    
        #*** Hub
        hubCost2002 = self.hub_mass * 4.25 # $/kg       
        hubCostEscalator = ppi.compute('IPPI_HUB')
        self.hub_cost = hubCost2002 * hubCostEscalator
    
        #*** NoseCone/Spinner
        spinnerCostEscalator = ppi.compute('IPPI_NAC')
        self.spinner_cost = spinnerCostEscalator * (5.57*self.spinner_mass)         

        self.hub_system_cost = self.hub_cost + self.pitch_system_cost + self.spinner_cost
        
        # derivatives
        self.d_hub_mass_d_diameter = 0.0
        self.d_pitch_mass_d_diameter = 0.0
        self.d_spinner_mass_d_diameter = 18.5
        self.d_system_mass_d_diameter = self.d_hub_mass_d_diameter + self.d_pitch_mass_d_diameter + self.d_spinner_mass_d_diameter
        
        self.d_hub_cost_d_diameter = 0.0
        self.d_pitch_cost_d_diameter = bearingCostEscalator * 2.28 * 2.6576 * (0.2106 * self.rotor_diameter**1.6576)
        self.d_spinner_cost_d_diameter = spinnerCostEscalator * (5.57*self.d_spinner_mass_d_diameter)
        self.d_system_cost_d_diameter = self.d_hub_cost_d_diameter + self.d_pitch_cost_d_diameter + self.d_spinner_cost_d_diameter

        self.d_hub_mass_d_blade_mass = 0.95402537 
        self.d_pitch_mass_d_blade_mass = 0.1295 *self.blade_number * (1+bearingHousingPct)
        self.d_spinner_mass_d_blade_mass = 0.0
        self.d_system_mass_d_blade_mass = self.d_hub_mass_d_blade_mass + self.d_pitch_mass_d_blade_mass + self.d_spinner_mass_d_blade_mass
        
        self.d_hub_cost_d_blade_mass = self.d_hub_mass_d_blade_mass * 4.25 * hubCostEscalator
        self.d_pitch_cost_d_blade_mass = 0.0
        self.d_spinner_cost_d_blade_mass = 0.0
        self.d_system_cost_d_blade_mass = self.d_hub_cost_d_blade_mass + self.d_pitch_cost_d_blade_mass + self.d_spinner_cost_d_blade_mass
        
    def list_deriv_vars(self):

        inputs = ['rotor_diameter', 'blade_mass']
        outputs = ['hub_mass', 'pitch_system_mass', 'spinner_mass', 'hub_system_mass', \
                   'hub_cost', 'pitch_system_cost', 'spinner_cost', 'hub_system_cost']
        
        return inputs, outputs
    
    def provideJ(self):
        
        self.J = np.array([[self.d_hub_mass_d_diameter, self.d_hub_mass_d_blade_mass],\
                           [self.d_pitch_mass_d_diameter, self.d_pitch_mass_d_blade_mass],\
                           [self.d_spinner_mass_d_diameter, self.d_spinner_mass_d_blade_mass],\
                           [self.d_system_mass_d_diameter, self.d_system_mass_d_blade_mass],\
                           [self.d_hub_cost_d_diameter, self.d_hub_cost_d_blade_mass],\
                           [self.d_pitch_cost_d_diameter, self.d_pitch_cost_d_blade_mass],\
                           [self.d_spinner_cost_d_diameter, self.d_spinner_cost_d_blade_mass],\
                           [self.d_system_cost_d_diameter, self.d_system_cost_d_blade_mass]])
        
        return self.J
        
#-----------------------------------------------------------------

def example():

    # simple test of module

    hub = hub_csm_component()
        
    # First test
    hub.blade_mass = 25614.377
    hub.rotor_diameter = 126.0
    hub.blade_number = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub csm component"
    print "Hub system mass: {0}".format(hub.hub_system_mass)
    print "Hub mass: {0}".format(hub.hub_mass)
    print "pitch system mass: {0}".format(hub.pitch_system_mass)
    print "spinner mass: {0}".format(hub.spinner_mass)
    print "Hub system cost: {0}".format(hub.hub_system_cost)

if __name__ == "__main__":

    example()