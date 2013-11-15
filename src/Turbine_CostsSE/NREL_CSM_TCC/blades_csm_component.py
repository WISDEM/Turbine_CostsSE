"""
blades_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from twister.models.csm.csmBlades import csmBlades

class blades_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advancedBlade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    bladeCost = Float(0.0, units='USD', iotype='out', desc='cost for a single wind turbine blade')
    bladeMass = Float(0.0, units='kg', iotype='out', desc='mass for a single wind turbine blade')

    def __init__(self):
        """
        OpenMDAO component to wrap blade model of the NREL Cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        advancedBlade : bool
          boolean for use of advanced blade curve
        year : int
          year of project start
        month : int
          month of project start
          
        Returns
        -------
        bladeCost : float
          cost for a single wind turbine blade [USD}
        bladeMass : float
          mass of a single rotor blade [kg]
        
        """
        super(blades_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade model of the NREL Cost and Scaling Model to estimate wind turbine blade cost and mass.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.compute(self.rotorDiameter, self.advancedBlade, self.year, self.month)

        self.bladeCost = self.blades.getCost()
        self.bladeMass = self.blades.getMass()
           
#-----------------------------------------------------------------

class blades_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advancedBlade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')

    # ------------- Outputs -------------- 
    bladeMass = Float(0.0, units='kg', iotype='out', desc='mass for a single wind turbine blade')

    def __init__(self):
        """
        OpenMDAO component to wrap blade mass model of the NREL Cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        advancedBlade : bool
          boolean for use of advanced blade curve
          
        Returns
        -------
        bladeMass : float
          mass of a single rotor blade [kg]
        
        """

        super(blades_mass_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade mass model of the NREL Cost and Scaling Model to estimate wind turbine blade mass.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.computeMass(self.rotorDiameter, self.advancedBlade)

        self.bladeMass = self.blades.getMass()
           
#-----------------------------------------------------------------

class blades_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotorDiameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advancedBlade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    bladeCost = Float(0.0, units='USD', iotype='out', desc='cost for a single wind turbine blade')


    def __init__(self):
        """
        OpenMDAO component to wrap blade model of the NREL Cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotorDiameter : float
          rotor diameter of the machine [m]
        advancedBlade : bool
          boolean for use of advanced blade curve
        year : int
          year of project start
        month : int
          month of project start
          
        Returns
        -------
        bladeCost : float
          cost for a single wind turbine blade [USD}
        
        """
        super(blades_cost_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade cost model of the NREL Cost and Scaling Model to estimate wind turbine blade cost.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.computeCost(self.rotorDiameter, self.advancedBlade, self.year, self.month)

        self.bladeCost = self.blades.getCost()
           
#-----------------------------------------------------------------

def example():
  
    # simple test of module

    blades = blades_csm_component()
        
    # First test
    blades.rotorDiameter = 126.0
    blades.advancedBlade = False
    blades.year = 2009
    blades.month = 12
    
    blades.execute()
    
    print "Blade csm component"
    print "Blade mass: {0}".format(blades.bladeMass)
    print "Blade cost: {0}".format(blades.bladeCost)
    
    # simple test of module

    blades = blades_mass_csm_component()
        
    # First test
    blades.rotorDiameter = 126.0
    blades.advancedBlade = False
    
    blades.execute()
    print "Blade mass csm component"    
    print "Blade mass: {0}".format(blades.bladeMass)
    
    # simple test of module

    blades = blades_cost_csm_component()
        
    # First test
    blades.rotorDiameter = 126.0
    blades.advancedBlade = False
    blades.year = 2009
    blades.month = 12
    
    blades.execute()
    print "Blade cost csm component"    
    print "Blade cost: {0}".format(blades.bladeCost)


if __name__ == "__main__":

    example()