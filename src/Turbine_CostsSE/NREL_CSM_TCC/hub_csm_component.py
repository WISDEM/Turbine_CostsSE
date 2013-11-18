"""
hub_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from NREL_CSM.csmHub import csmHub

class hub_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    blade_mass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
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

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        blade_mass : float
          mass of an individual blade [kg]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        hub_system_cost : float
          hub system cost [USD]
        hub_system_mass : float
          hub system mass [kg]
        hub_cost : float
          hub cost for component [USD]
        hub_mass : float
          hub mass for component [kg]
        pitch_system_cost : float
          pitch system cost [USD]
        pitch_system_mass : float
          pitch system mass [kg]
        spinner_cost : float
          spinner / nose cone cost [USD]
        spinner_mass : float
          spinner / nose cone mass [kg]    
        """

        super(hub_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL _cost and Scaling model to compute hub system component masses and costs.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.compute(self.blade_mass, self.rotor_diameter, self.bladeNumber, self.year, self.month)

        self.hub_system_cost = self.hub.getCost()
        self.hub_system_mass = self.hub.getMass()
        self.hub_cost = self.hub.hub_cost
        self.hub_mass = self.hub.hub_mass
        self.pitch_system_mass = self.hub.pitchSys_mass
        self.pitch_system_cost = self.hub.pitchSys_cost
        self.spinner_mass = self.hub.spinner_mass
        self.spinner_cost = self.hub.spinner_cost
           
#-----------------------------------------------------------------

class hub_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    blade_mass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    hub_system_mass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    hub_mass = Float(0.0, units='kg', iotype='out', desc='hub mass')
    pitch_system_mass = Float(0.0, units='kg', iotype='out', desc='pitch system mass')
    spinner_mass = Float(0.0, units='kg', iotype='out', desc='spinner mass')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL _cost and Scaling Model (csmHub.py)

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        blade_mass : float
          mass of an individual blade [kg]
        
        Returns
        -------
        hub_system_mass : float
          hub system mass [kg]
        hub_mass : float
          hub mass for component [kg]
        pitch_system_mass : float
          pitch system mass [kg]
        spinner_mass : float
          spinner / nose cone mass [kg]    
        """
        super(hub_mass_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL _cost and Scaling model to compute hub system component masses.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.compute_mass(self.blade_mass, self.rotor_diameter, self.bladeNumber)

        self.hub_system_mass = self.hub.getMass()
        self.hub_mass = self.hub.hub_mass
        self.pitch_system_mass = self.hub.pitchSys_mass
        self.spinner_mass = self.hub.spinner_mass
           
#-----------------------------------------------------------------

class hub_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    spinner_mass = Float(1810.5, units='kg', iotype='out', desc='spinner / nose cone mass')
    hub_mass = Float(22519.7, units='kg', iotype='in', desc='hub mass')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    hub_system_cost = Float(0.0, units='USD', iotype='out', desc='hub system cost')
    hub_cost = Float(0.0, units='USD', iotype='out', desc='hub cost')
    pitch_system_cost = Float(0.0, units='USD', iotype='out', desc='pitch system cost')
    spinner_cost = Float(0.0, units='USD', iotype='out', desc='spinner / nose cone cost')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL _cost and Scaling Model (csmHub.py)

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        hub_mass : float
          hub mass for component [kg]
        spinner_mass : float
          spinner / nose cone mass [kg] 
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        hub_system_cost : float
          hub system cost [USD]
        hub_cost : float
          hub cost for component [USD]
        pitch_system_cost : float
          pitch system cost [USD]
        spinner_cost : float
          spinner / nose cone cost [USD]  
        """
        super(hub_cost_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL _cost and Scaling model to compute hub system component costs.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.compute_cost(self.rotor_diameter, self.year, self.month, self.hub_mass, self.spinner_mass)

        self.hub_system_cost = self.hub.getCost()
        self.hub_cost = self.hub.hub_cost
        self.pitch_system_cost = self.hub.pitchSys_cost
        self.spinner_cost = self.hub.spinner_cost
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    hub = hub_csm_component()
        
    # First test
    hub.blade_mass = 17650.67
    hub.rotor_diameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub csm component"
    print "Hub system mass: {0}".format(hub.hub_system_mass)
    print "Hub mass: {0}".format(hub.hub_mass)
    print "pitch system mass: {0}".format(hub.pitch_system_mass)
    print "spinner mass: {0}".format(hub.spinner_mass)
    print "Hub system cost: {0}".format(hub.hub_system_cost)
    
    # simple test of module

    hub = hub_mass_csm_component()
        
    # First test
    hub.blade_mass = 17650.67
    hub.rotor_diameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub mass csm component"
    print "Hub system mass: {0}".format(hub.hub_system_mass)
    
    # simple test of module

    hub = hub_cost_csm_component()
        
    # First test
    hub.blade_mass = 17650.67
    hub.rotor_diameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub cost csm component"
    print "Hub system cost: {0}".format(hub.hub_system_cost)


if __name__ == "__main__":

    example()