"""
tower_csm_component.py

Created by NWTC Systems Engineering Sub-Task on 2012-08-01.
Copyright (c) NREL. All rights reserved.
"""

from openmdao.main.api import Component, Assembly, set_as_top, VariableTree
from openmdao.main.datatypes.api import Int, Bool, Float, Array, VarTree

from commonse.config import *
import numpy as np

class tower_csm_component(Component):
    """
       Component to wrap python code for NREL cost and scaling model for a wind turbine tower
    """

    # ---- Design Variables -------------- 
    
    # Varaiables
    rotor_diameter = Float(126.0, units = 'm', iotype='in', desc= 'rotor diameter of the machine') 
    hub_height = Float(90.0, units = 'm', iotype='in', desc = 'hub height of machine')
    
    # Parameters
    year = Int(2009, iotype='in', desc = 'year of project start')
    month = Int(12, iotype='in', desc = 'month of project start')
    advanced_tower = Bool(False, iotype='in', desc = 'advanced tower configuration')

    # Outputs 
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
        advanced : bool
          advanced tower configuration
        
        Returns
        -------
        tower_cost : float
          cost for a tower [USD]
        tower_mass : float
          mass for a turbine tower [kg]       
        """        

        super(tower_csm_component, self).__init__()

    def execute(self):
        """
        Executes the tower model of the NREL _cost and Scaling Model.
        """
        print "In {0}.execute()...".format(self.__class__)

        windpactMassSlope = 0.397251147546925
        windpactMassInt   = -1414.381881
        
        if self.advanced_tower:
           windpactMassSlope = 0.269380169
           windpactMassInt = 1779.328183

        self.tower_mass = windpactMassSlope * np.pi * (self.rotor_diameter/2.)**2 * self.hub_height + windpactMassInt

        ppi.curr_yr = curr_yr
        ppi.curr_mon = curr_mon

        twrCostEscalator  = 1.5944
        twrCostEscalator  = ppi.compute('IPPI_TWR')
        twrCostCoeff      = 1.5 # $/kg    

        self.towerCost2002 = self.tower_mass * twrCostCoeff               
        self.tower_cost = self.towerCost2002 * twrCostEscalator
        
        # derivatives
        self.d_mass_d_diameter = 2 * windpactMassSlope * np.pi * (self.rotor_diameter/2.) * (1/2.) * self.hub_height
        self.d_mass_d_hheight = windpactMassSlope * np.pi * (self.rotor_diameter/2.)**2
        self.d_cost_d_diameter = twrCostCoeff * twrCostEscalator * self.d_mass_d_diameter
        self.d_cost_d_hheight = twrCostCoeff * twrCostEscalator * self.d_mass_d_hheight
    
    def linearize(self):
        
        self.J = np.array([[self.d_mass_d_diameter, self.d_mass_d_hheight], [self.d_cost_d_diameter, self.d_cost_d_hheight]])
    
    def provideJ(self):

        inputs = ['rotor_diameter', 'hub_height']       
        outputs = ['tower_mass', 'tower_cost']
        
        return inputs, outputs, self.J        
          
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

if __name__ == "__main__":

    example()