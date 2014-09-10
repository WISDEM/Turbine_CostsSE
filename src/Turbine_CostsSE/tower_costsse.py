"""
tower_costsse.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from commonse.config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
import numpy as np

from fusedwind.plant_cost.fused_tcc import FullTowerCostModel, FullTowerCostAggregator, BaseComponentCostModel, configure_full_twcc
from fusedwind.interface import implement_base

#-------------------------------------------------------------------------------
@implement_base(BaseComponentCostModel)
class TowerCost(Component):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # Outputs
    cost = Float(0.0, iotype='out', desc='Overall wind turbine component capial costs excluding transportation costs')

    def __init__(self):
        '''
        Initial computation of the costs for the wind turbine tower component.

        '''

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        # assign input variables
        ppi.curr_yr   = self.year
        ppi.curr_mon   = self.month

        twrCostEscalator  = ppi.compute('IPPI_TWR')

        twrCostCoeff      = 1.5 # $/kg

        self.towerCost2002 = self.tower_mass * twrCostCoeff
        self.cost = self.towerCost2002 * twrCostEscalator

        # derivatives
        self.d_cost_d_tower_mass = twrCostEscalator * twrCostCoeff

    def list_deriv_vars(self):

        inputs = ['tower_mass']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_tower_mass]])

        return self.J


#-------------------------------------------------------------------------------
@implement_base(FullTowerCostAggregator)
class TowerCostAdder(Component):

    # variables
    tower_cost = Float(iotype='in', units='USD', desc='component cost')
    
    # returns
    cost = Float(iotype='out', units='USD', desc='component cost') 

    def __init__(self):

        Component.__init__(self)

        #controls what happens if derivatives are missing
        self.missing_deriv_policy = 'assume_zero'

    def execute(self):

        partsCost = self.tower_cost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)
        overheadCostMultiplier = 0.0 # (24/72)
        profitMultiplier = 0.0
        transportMultiplier = 0.0

        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)

        # derivatives
        self.d_cost_d_tower_cost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

    def list_deriv_vars(self):

        inputs = ['tower_cost']
        outputs = ['cost']

        return inputs, outputs

    def provideJ(self):

        # Jacobian
        self.J = np.array([[self.d_cost_d_tower_cost]])

        return self.J

@implement_base(FullTowerCostModel)
class Tower_CostsSE(Assembly):

    # variables
    tower_mass = Float(iotype='in', units='kg', desc='tower mass [kg]')

    # parameters
    year = Int(iotype='in', desc='Current Year')
    month = Int(iotype='in', desc='Current Month')

    # returns
    cost = Float(iotype='out', units='USD', desc='component cost')

    def configure(self):

        configure_full_twcc(self)

        self.replace('towerCC', TowerCost())
        self.replace('twrcc', TowerCostAdder())

        self.connect('tower_mass', 'towerCC.tower_mass')
        self.connect('year', 'towerCC.year')
        self.connect('month', 'towerCC.month')


#-------------------------------------------------------------------------------

def example():

    # simple test of module
    tower = Tower_CostsSE()

    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    tower.tower_mass = 434559.0
    tower.year = 2009
    tower.month =  12

    tower.run()

    print "Tower cost is ${0:.2f} USD".format(tower.cost) # $987180.30

if __name__ == "__main__":

    example()