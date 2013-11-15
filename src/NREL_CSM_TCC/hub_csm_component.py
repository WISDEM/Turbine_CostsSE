"""
hub_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.csm.csmHub import csmHub

class hub_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    bladeMass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    hubSystemCost = Float(0.0, units='USD', iotype='out', desc='hub system cost')
    hubSystemMass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    hubCost = Float(0.0, units='USD', iotype='out', desc='hub cost')
    hubMass = Float(0.0, units='kg', iotype='out', desc='hub mass')
    pitchSystemCost = Float(0.0, units='USD', iotype='out', desc='pitch system cost')
    pitchSystemMass = Float(0.0, units='kg', iotype='out', desc='pitch system mass')
    spinnerCost = Float(0.0, units='USD', iotype='out', desc='spinner / nose cone cost')
    spinnerMass = Float(0.0, units='kg', iotype='out', desc='spinner / nose cone mass')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL Cost and Scaling Model (csmHub.py)

        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        bladeMass : float
          mass of an individual blade [kg]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        hubSystemCost : float
          hub system cost [USD]
        hubSystemMass : float
          hub system mass [kg]
        hubCost : float
          hub cost for component [USD]
        hubMass : float
          hub mass for component [kg]
        pitchSystemCost : float
          pitch system cost [USD]
        pitchSystemMass : float
          pitch system mass [kg]
        spinnerCost : float
          spinner / nose cone cost [USD]
        spinnerMass : float
          spinner / nose cone mass [kg]    
        """

        super(hub_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL Cost and Scaling model to compute hub system component masses and costs.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.compute(self.bladeMass, self.rotorDiameter, self.bladeNumber, self.year, self.month)

        self.hubSystemCost = self.hub.getCost()
        self.hubSystemMass = self.hub.getMass()
        self.hubCost = self.hub.hubCost
        self.hubMass = self.hub.hubMass
        self.pitchSystemMass = self.hub.pitchSysMass
        self.pitchSystemCost = self.hub.pitchSysCost
        self.spinnerMass = self.hub.spinnerMass
        self.spinnerCost = self.hub.spinnerCost
           
#-----------------------------------------------------------------

class hub_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    bladeMass = Float(17650.67, units='kg', iotype='in', desc='mass of an individual blade')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    hubSystemMass = Float(0.0, units='kg', iotype='out', desc='hub system mass')
    hubMass = Float(0.0, units='kg', iotype='out', desc='hub mass')
    pitchSystemMass = Float(0.0, units='kg', iotype='out', desc='pitch system mass')
    spinnerMass = Float(0.0, units='kg', iotype='out', desc='spinner mass')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL Cost and Scaling Model (csmHub.py)

        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        bladeMass : float
          mass of an individual blade [kg]
        
        Returns
        -------
        hubSystemMass : float
          hub system mass [kg]
        hubMass : float
          hub mass for component [kg]
        pitchSystemMass : float
          pitch system mass [kg]
        spinnerMass : float
          spinner / nose cone mass [kg]    
        """
        super(hub_mass_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL Cost and Scaling model to compute hub system component masses.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.computeMass(self.bladeMass, self.rotorDiameter, self.bladeNumber)

        self.hubSystemMass = self.hub.getMass()
        self.hubMass = self.hub.hubMass
        self.pitchSystemMass = self.hub.pitchSysMass
        self.spinnerMass = self.hub.spinnerMass
           
#-----------------------------------------------------------------

class hub_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine hub
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    bladeNumber = Int(3, iotype='in', desc= 'number of rotor blades')
    spinnerMass = Float(1810.5, units='kg', iotype='out', desc='spinner / nose cone mass')
    hubMass = Float(22519.7, units='kg', iotype='in', desc='hub mass')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    hubSystemCost = Float(0.0, units='USD', iotype='out', desc='hub system cost')
    hubCost = Float(0.0, units='USD', iotype='out', desc='hub cost')
    pitchSystemCost = Float(0.0, units='USD', iotype='out', desc='pitch system cost')
    spinnerCost = Float(0.0, units='USD', iotype='out', desc='spinner / nose cone cost')

    def __init__(self):
        """
        OpenMDAO component to wrap hub model of the NREL Cost and Scaling Model (csmHub.py)

        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        bladeNumber : int
          number of rotor blades
        hubMass : float
          hub mass for component [kg]
        spinnerMass : float
          spinner / nose cone mass [kg] 
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        hubSystemCost : float
          hub system cost [USD]
        hubCost : float
          hub cost for component [USD]
        pitchSystemCost : float
          pitch system cost [USD]
        spinnerCost : float
          spinner / nose cone cost [USD]  
        """
        super(hub_cost_csm_component, self).__init__()
        
        self.hub = csmHub()

    def execute(self):
        """
        Executes hub model of the NREL Cost and Scaling model to compute hub system component costs.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.hub.computeCost(self.rotorDiameter, self.year, self.month, self.hubMass, self.spinnerMass)

        self.hubSystemCost = self.hub.getCost()
        self.hubCost = self.hub.hubCost
        self.pitchSystemCost = self.hub.pitchSysCost
        self.spinnerCost = self.hub.spinnerCost
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    hub = hub_csm_component()
        
    # First test
    hub.bladeMass = 17650.67
    hub.rotorDiameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub csm component"
    print "Hub system mass: {0}".format(hub.hubSystemMass)
    print "Hub mass: {0}".format(hub.hubMass)
    print "pitch system mass: {0}".format(hub.pitchSystemMass)
    print "spinner mass: {0}".format(hub.spinnerMass)
    print "Hub system cost: {0}".format(hub.hubSystemCost)
    
    # simple test of module

    hub = hub_mass_csm_component()
        
    # First test
    hub.bladeMass = 17650.67
    hub.rotorDiameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub mass csm component"
    print "Hub system mass: {0}".format(hub.hubSystemMass)
    
    # simple test of module

    hub = hub_cost_csm_component()
        
    # First test
    hub.bladeMass = 17650.67
    hub.rotorDiameter = 126.0
    hub.bladeNumber = 3
    hub.year = 2009
    hub.month = 12
    
    hub.execute()
    
    print "Hub cost csm component"
    print "Hub system cost: {0}".format(hub.hubSystemCost)


if __name__ == "__main__":

    example()