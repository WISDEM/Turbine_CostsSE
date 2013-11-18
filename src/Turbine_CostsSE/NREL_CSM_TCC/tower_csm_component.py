"""
tower_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from NREL_CSM.csmTower import csmTower

class tower_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hub_height = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    tower_cost = Float(0.0, units='USD', iotype='out', desc='cost for a tower')
    tower_mass = Float(0.0, units='kg', iotype='out', desc='mass for a turbine tower')

    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL _cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        hub_height : float
          hub height of machine [m]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        tower_cost : float
          cost for a tower [USD]
        tower_mass : float
          mass for a turbine tower [kg]       
        """        

        super(tower_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.compute(self.rotor_diameter, self.hub_height, self.year, self.month)

        self.tower_cost = self.tower.getCost()
        self.tower_mass = self.tower.getMass()
           
#-----------------------------------------------------------------

class tower_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    tower_mass = Float(0.0, units='kg', iotype='in', desc='mass for a turbine tower')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    tower_cost = Float(0.0, units='USD', iotype='out', desc='cost for a tower')


    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL _cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        tower_mass : float
          mass for a turbine tower [kg]
        year : int
          year of project start
        month : int
          month of project start
        
        Returns
        -------
        tower_cost : float
          cost for a tower [USD]    
        """ 
        super(tower_cost_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.compute_cost(self.year, self.month,self.tower_mass)

        self.tower_cost = self.tower.getCost()
           
#-----------------------------------------------------------------

class tower_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hub_height = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')

    # ------------- Outputs -------------- 

    tower_mass = Float(0.0, units='kg', iotype='out', desc='mass for a turbine tower')

    def __init__(self):
        """
        OpenMDAO component to wrap tower model based of the NREL _cost and Scaling Model data (csmTower.py).

        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        hub_height : float
          hub height of machine [m]
        
        Returns
        -------
        tower_mass : float
          mass for a turbine tower [kg]       
        """  
        super(tower_mass_csm_component, self).__init__()
        
        self.tower = csmTower()

    def execute(self):
        """
        Executes the tower model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.tower.compute_mass(self.rotor_diameter, self.hub_height)

        self.tower_mass = self.tower.getMass()
           
#-----------------------------------------------------------------

def example():

    # simple test of module

    tower = tower_csm_component()
        
    # First test
    tower.rotor_diameter = 126.0
    tower.hub_height = 90.0
    tower.year = 2009
    tower.month = 12
    
    tower.execute()
    
    print "Tower csm component"
    print "Tower mass: {0}".format(tower.tower_mass)
    print "Tower cost: {0}".format(tower.tower_cost)

    # simple test of module

    tower = tower_cost_csm_component()
        
    # First test
    tower.tower_mass = 444384.16
    tower.year = 2009
    tower.month = 12
    
    tower.execute()

    print "Tower cost csm component"
    print "Tower cost: {0}".format(tower.tower_cost)

    # simple test of module

    tower = tower_mass_csm_component()
        
    # First test
    tower.rotor_diameter = 126.0
    tower.hub_height = 90.0
    
    tower.execute()
    
    print "Tower mass csm component"
    print "Tower mass: {0}".format(tower.tower_mass)

if __name__ == "__main__":

    example()