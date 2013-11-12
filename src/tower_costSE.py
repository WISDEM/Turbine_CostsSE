"""
towercost.py

Created by George Scott on 2012-08-01.
Modified by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
import numpy as np

#-------------------------------------------------------------------------------        

class TowerCost(Component):

    # variables
    towerMass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    
    # parameters
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='Blade cost for an individual blade')    

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine tower component.       
        
        Parameters
        ----------
        towerMass : float
          mass [kg] of the wind turbine tower
        curr_yr : int
          Project start year
        curr_mon : int
          Project start month        

        Returns
        -------
        cost : float
          component cost [USD]       
        '''
        
        super(TowerCost, self).__init__()
     
    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.curr_yr
        ppi.curr_mon   = self.curr_mon

        twrCostEscalator  = ppi.compute('IPPI_TWR')
        
        twrCostCoeff      = 1.5 # $/kg    
        
        self.towerCost2002 = self.towerMass * twrCostCoeff               
        self.cost = self.towerCost2002 * twrCostEscalator
        
        # derivatives
        d_cost_d_towerMass = twrCostEscalator * twrCostCoeff
        
        # Jacobian
        self.J = np.array([[d_cost_d_towerMass]])

    def provideJ(self):

        input_keys = ['towerMass']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)        
        
#-------------------------------------------------------------------------------       

def example():

    # simple test of module
    tower = TowerCost()
    
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    tower.towerMass = 434559.0
    tower.curr_yr = 2009
    tower.curr_mon =  12
    
    tower.run()
    
    print "Tower cost is ${0:.2f} USD".format(tower.cost) # $987180.30

if __name__ == "__main__":  

    example()