"""
tower_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.csm.csmTower import csmTower

class tower_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hubHeight = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    towerCost = Float(0.0, units='USD', iotype='out', desc='cost for a tower')
    towerMass = Float(0.0, units='kg', iotype='out', desc='mass for a turbine tower')

    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL Cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        hubHeight : float
          hub height of machine [m]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        towerCost : float
          cost for a tower [USD]
        towerMass : float
          mass for a turbine tower [kg]       
        """        

        super(tower_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL Cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.compute(self.rotorDiameter, self.hubHeight, self.year, self.month)

        self.towerCost = self.tower.getCost()
        self.towerMass = self.tower.getMass()
           
#-----------------------------------------------------------------

class tower_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    towerMass = Float(0.0, units='kg', iotype='in', desc='mass for a turbine tower')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    towerCost = Float(0.0, units='USD', iotype='out', desc='cost for a tower')


    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL Cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        towerMass : float
          mass for a turbine tower [kg]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        towerCost : float
          cost for a tower [USD]    
        """ 
        super(tower_cost_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL Cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.computeCost(self.year, self.month,self.towerMass)

        self.towerCost = self.tower.getCost()
           
#-----------------------------------------------------------------

class tower_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hubHeight = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')

    # ------------- Outputs -------------- 

    towerMass = Float(0.0, units='kg', iotype='out', desc='mass for a turbine tower')

    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL Cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        hubHeight : float
          hub height of machine [m]
        
        Returns
        -------
        towerMass : float
          mass for a turbine tower [kg]       
        """  
        super(tower_mass_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL Cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.computeMass(self.rotorDiameter, self.hubHeight)

        self.towerMass = self.tower.getMass()
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    tower = tower_csm_component()
        
    # First test
    tower.rotorDiameter = 126.0
    tower.hubHeight = 90.0
    tower.year = 2009
    tower.month = 12
    
    tower.execute()
    
    print "Tower csm component"
    print "Tower mass: {0}".format(tower.towerMass)
    print "Tower cost: {0}".format(tower.towerCost)

    # simple test of module

    tower = tower_cost_csm_component()
        
    # First test
    tower.towerMass = 444384.16
    tower.year = 2009
    tower.month = 12
    
    tower.execute()

    print "Tower cost csm component"
    print "Tower cost: {0}".format(tower.towerCost)

    # simple test of module

    tower = tower_mass_csm_component()
        
    # First test
    tower.rotorDiameter = 126.0
    tower.hubHeight = 90.0
    
    tower.execute()
    
    print "Tower mass csm component"
    print "Tower mass: {0}".format(tower.towerMass)

if __name__ == "__main__":

    example()