"""
blades_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

import sys

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from NREL_CSM.csmBlades import csmBlades

class blades_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    blade_cost = Float(0.0, units='USD', iotype='out', desc='cost for a single wind turbine blade')
    blade_mass = Float(0.0, units='kg', iotype='out', desc='mass for a single wind turbine blade')

    def __init__(self):
        """
        OpenMDAO component to wrap blade model of the NREL _cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        advanced_blade : bool
          boolean for use of advanced blade curve
        year : int
          year of project start
        month : int
          month of project start
          
        Returns
        -------
        blade_cost : float
          cost for a single wind turbine blade [USD}
        blade_mass : float
          mass of a single rotor blade [kg]
        
        """
        super(blades_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade model of the NREL _cost and Scaling Model to estimate wind turbine blade cost and mass.
        """
        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.compute(self.rotor_diameter, self.advanced_blade, self.year, self.month)

        self.blade_cost = self.blades.getCost()
        self.blade_mass = self.blades.getMass()
           
#-----------------------------------------------------------------

class blades_mass_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')

    # ------------- Outputs -------------- 
    blade_mass = Float(0.0, units='kg', iotype='out', desc='mass for a single wind turbine blade')

    def __init__(self):
        """
        OpenMDAO component to wrap blade mass model of the NREL _cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        advanced_blade : bool
          boolean for use of advanced blade curve
          
        Returns
        -------
        blade_mass : float
          mass of a single rotor blade [kg]
        
        """

        super(blades_mass_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade mass model of the NREL _cost and Scaling Model to estimate wind turbine blade mass.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.compute_mass(self.rotor_diameter, self.advanced_blade)

        self.blade_mass = self.blades.getMass()
           
#-----------------------------------------------------------------

class blades_cost_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """

    # ---- Design Variables -------------- 
    
    # Turbine Configuration
    # rotor
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')
    
    # Plant Configuration
    year = Int(2009, units = 'yr', iotype='in', desc = 'year of project start')
    month = Int(12, units = 'mon', iotype='in', desc = 'month of project start')

    # ------------- Outputs -------------- 
  
    blade_cost = Float(0.0, units='USD', iotype='out', desc='cost for a single wind turbine blade')


    def __init__(self):
        """
        OpenMDAO component to wrap blade model of the NREL _cost and Scaling Model (csmBlades.py)
        
        Parameters
        ----------
        rotor_diameter : float
          rotor diameter of the machine [m]
        advanced_blade : bool
          boolean for use of advanced blade curve
        year : int
          year of project start
        month : int
          month of project start
          
        Returns
        -------
        blade_cost : float
          cost for a single wind turbine blade [USD}
        
        """
        super(blades_cost_csm_component, self).__init__()
        
        self.blades = csmBlades()

    def execute(self):
        """
        Executes Blade cost model of the NREL _cost and Scaling Model to estimate wind turbine blade cost.
        """

        print "In {0}.execute()...".format(self.__class__)
        
        self.blades.compute_cost(self.rotor_diameter, self.advanced_blade, self.year, self.month)

        self.blade_cost = self.blades.getCost()
           
#-----------------------------------------------------------------

def example():
  
    # simple test of module

    blades = blades_csm_component()
        
    # First test
    blades.rotor_diameter = 126.0
    blades.advanced_blade = False
    blades.year = 2009
    blades.month = 12
    
    blades.execute()
    
    print "Blade csm component"
    print "Blade mass: {0}".format(blades.blade_mass)
    print "Blade cost: {0}".format(blades.blade_cost)
    
    # simple test of module

    blades = blades_mass_csm_component()
        
    # First test
    blades.rotor_diameter = 126.0
    blades.advanced_blade = False
    
    blades.execute()
    print "Blade mass csm component"    
    print "Blade mass: {0}".format(blades.blade_mass)
    
    # simple test of module

    blades = blades_cost_csm_component()
        
    # First test
    blades.rotor_diameter = 126.0
    blades.advanced_blade = False
    blades.year = 2009
    blades.month = 12
    
    blades.execute()
    print "Blade cost csm component"    
    print "Blade cost: {0}".format(blades.blade_cost)


if __name__ == "__main__":

    example()