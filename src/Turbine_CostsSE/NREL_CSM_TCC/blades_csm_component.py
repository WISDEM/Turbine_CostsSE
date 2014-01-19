"""
blades_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from commonse.config import *
import numpy as np

class blades_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine blade
    """
    
    # Variables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    advanced_blade = Bool(False, iotype='in', desc = 'boolean for use of advanced blade curve')

    # Outputs
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

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):
        """
        Executes Blade model of the NREL _cost and Scaling Model to estimate wind turbine blade cost and mass.
        """
        print "In {0}.execute()...".format(self.__class__)

        if (self.advanced_blade == True):
            massCoeff = 0.4948
            massExp   = 2.5300
        else:
            massCoeff = 0.1452 
            massExp   = 2.9158
        
        self.blade_mass = (massCoeff*(self.rotor_diameter/2.0)**massExp)

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        ppi_labor  = ppi.compute('IPPI_BLL')

        if (self.advanced_blade == True):
            ref_yr = ppi.ref_yr
            ppi.ref_yr = 2003
            ppi_mat   = ppi.compute('IPPI_BLA')
            ppi.ref_yr = ref_yr
            slopeR3   = 0.4019376
            intR3     = -21051.045983
        else:
            ppi_mat   = ppi.compute('IPPI_BLD')
            slopeR3   = 0.4019376
            intR3     = -955.24267
            
        laborCoeff    = 2.7445
        laborExp      = 2.5025
        
        bladeCostCurrent = ( (slopeR3*(self.rotor_diameter/2.0)**3.0 + (intR3))*ppi_mat + \
                                  (laborCoeff*(self.rotor_diameter/2.0)**laborExp)*ppi_labor    ) / (1.0-0.28)
        self.blade_cost = bladeCostCurrent
    
        # derivatives
        self.d_mass_d_diameter = massExp * (massCoeff*(self.rotor_diameter/2.0)**(massExp-1))* (1/2.)
        self.d_cost_d_diameter = (3.0*(slopeR3*(self.rotor_diameter/2.0)**2.0 )*ppi_mat * (1/2.) + \
                                 (laborExp * laborCoeff*(self.rotor_diameter/2.0)**(laborExp-1))*ppi_labor * (1/2.)) / (1.0-0.28)
 
    def list_deriv_vars(self):

    	  inputs = ('rotor_diameter')
    	  outputs = ('blade_mass', 'blade_cost')
    	  
    	  return inputs, outputs
    
    def provideJ(self):
    	  
    	  self.J = np.array([[self.d_mass_d_diameter],[self.d_cost_d_diameter]])    	
    	  
    	  return self.J
         
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

    blades.advanced_blade = True

    blades.execute()
    
    print "Blade csm component, advanced blade"
    print "Blade mass: {0}".format(blades.blade_mass)
    print "Blade cost: {0}".format(blades.blade_cost)

if __name__ == "__main__":

    example()