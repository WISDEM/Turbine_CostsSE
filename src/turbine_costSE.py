"""
turbinecost.py

Created by Katherine Dykes 2012.
Copyright (c) NREL. All rights reserved.
"""

from config import *
from openmdao.main.api import Component, Assembly
from openmdao.main.datatypes.api import Array, Float, Bool, Int
import numpy as np

from rotor_costsSE import Rotor_CostsSE
from nacelle_costsSE import Nacelle_CostsSE
from tower_costSE import TowerCost

#-------------------------------------------------------------------------------        

class Turbine_CostSE(Assembly):

    '''
    Initial computation of the costs for the wind turbine.

    Parameters
    ----------
    bladeMass : float
      blade mass [kg]
    hubMass : float
      hub mass [kg]
    pitchSystemMass : float
      pitch system mass [kg]
    spinnerMass : float
      spinner mass [kg]
    lowSpeedShaftMass : float
      Low speed shaft mass [kg]
    mainBearingsMass : float
      bearing mass [kg]
    secondBearingsMass : float
      bearing mass [kg]
    gearboxMass : float
      Gearbox mass [kg]
    highSpeedSideMass : float
      High speed side mass [kg]
    bedplateMass : float
      Bedplate mass [kg]
    yawSystemMass : float
      Yaw system mass [kg]
    towerMass : float
      mass [kg] of the wind turbine tower
    machineRating : float
      Machine rating for turbine [kW]
    bladeNumber : int
      Number of blades on rotor
    advanced : bool
      boolean for advanced (using carbon) or basline (all fiberglass) blade
    drivetrainDesign : int
      machine configuration 1 conventional, 2 medium speed, 3 multi-gen, 4 direct-drive
    offshore : bool
      boolean true if it is offshore
    crane : bool
        boolean for crane present on-board
    curr_yr : int
      Project start year
    curr_mon : int
      Project start month
      
    Returns
    -------
    cost : float
      overall turbine cost [USD]        
    '''

    # variables
    bladeMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    hubMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    pitchSystemMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    spinnerMass = Float(iotype='in', units='kg', desc='component mass [kg]')
    lowSpeedShaftMass = Float(iotype='in', units='kg', desc='component mass')
    mainBearingMass = Float(iotype='in', units='kg', desc='component mass')
    secondBearingMass = Float(iotype='in', units='kg', desc='component mass')
    gearboxMass = Float(iotype='in', units='kg', desc='component mass')
    highSpeedSideMass = Float(iotype='in', units='kg', desc='component mass')
    generatorMass = Float(iotype='in', units='kg', desc='component mass')
    bedplateMass = Float(iotype='in', units='kg', desc='component mass')
    yawSystemMass = Float(iotype='in', units='kg', desc='component mass')
    towerMass = Float(iotype='in', units='kg', desc='tower mass [kg]')
    machineRating = Float(iotype='in', units='kW', desc='machine rating')
    
    # parameters
    bladeNumber = Int(iotype='in', desc='number of rotor blades')
    advanced = Bool(True, iotype='in', desc='advanced (True) or traditional (False) blade design') 
    drivetrainDesign = Int(iotype='in', desc='type of gearbox based on drivetrain type: 1 = standard 3-stage gearbox, 2 = single-stage, 3 = multi-gen, 4 = direct drive')
    crane = Bool(iotype='in', desc='flag for presence of onboard crane')
    offshore = Bool(iotype='in', desc='flag for offshore site')
    curr_yr = Int(iotype='in', desc='Current Year')
    curr_mon = Int(iotype='in', desc='Current Month')

    def configure(self):

        # select components
        self.add('rotorCostSE', Rotor_CostsSE())
        self.add('nacelleCostSE', Nacelle_CostsSE())
        self.add('towerCostSE', TowerCost())
        self.add('turbineCostAdder', TurbineCostAdder())
        
        # workflow
        self.driver.workflow.add(['rotorCostSE', 'nacelleCostSE', 'towerCostSE', 'turbineCostAdder'])
        
        # connect inputs
        self.connect('bladeMass', 'rotorCostSE.bladeMass')
        self.connect('hubMass', 'rotorCostSE.hubMass')
        self.connect('pitchSystemMass', 'rotorCostSE.pitchSystemMass')
        self.connect('spinnerMass', 'rotorCostSE.spinnerMass')
        self.connect('bladeNumber', 'rotorCostSE.bladeNumber')
        self.connect('advanced', 'rotorCostSE.advanced')
        self.connect('lowSpeedShaftMass', 'nacelleCostSE.lowSpeedShaftMass')
        self.connect('mainBearingMass', 'nacelleCostSE.mainBearingMass')
        self.connect('secondBearingMass', 'nacelleCostSE.secondBearingMass')
        self.connect('gearboxMass', 'nacelleCostSE.gearboxMass')
        self.connect('highSpeedSideMass', 'nacelleCostSE.highSpeedSideMass')
        self.connect('generatorMass', 'nacelleCostSE.generatorMass')
        self.connect('bedplateMass', ['nacelleCostSE.bedplateMass'])
        self.connect('yawSystemMass', 'nacelleCostSE.yawSystemMass')
        self.connect('machineRating', ['nacelleCostSE.machineRating'])
        self.connect('drivetrainDesign', ['nacelleCostSE.drivetrainDesign'])
        self.connect('crane', 'nacelleCostSE.crane')
        self.connect('offshore', ['nacelleCostSE.offshore', 'turbineCostAdder.offshore'])
        self.connect('towerMass', 'towerCostSE.towerMass')
        self.connect('curr_yr', ['rotorCostSE.curr_yr', 'nacelleCostSE.curr_yr', 'towerCostSE.curr_yr'])
        self.connect('curr_mon', ['rotorCostSE.curr_mon', 'nacelleCostSE.curr_mon', 'towerCostSE.curr_mon'])
        
        # connect components
        self.connect('rotorCostSE.cost', 'turbineCostAdder.rotorCost')
        self.connect('nacelleCostSE.cost', 'turbineCostAdder.nacelleCost')
        self.connect('towerCostSE.cost', 'turbineCostAdder.towerCost')
        
        # create passthroughs
        self.create_passthrough('turbineCostAdder.cost')


#-------------------------------------------------------------------------------

class TurbineCostAdder(Component):

    # variables
    rotorCost = Float(iotype='in', units='USD', desc='rotor cost')
    nacelleCost = Float(iotype='in', units='USD', desc='nacelle cost')
    towerCost = Float(iotype='in', units='USD', desc='tower cost')
    
    # parameters
    offshore = Bool(iotype='in', desc='flag for offshore site')

    # return
    cost = Float(iotype='out', units='USD', desc='turbine overall cost')

    def __init__(self):
      
        '''
        Turbine cost adder
        
        rotorCost : float
          rotor cost [USD]
        nacelleCost : float
          nacelle cost [USD]
        towerCost : float
          tower cost [USD]

        Returns
        -------
        cost : float
          overall rotor cost [USD]   
        '''   
        
        super(TurbineCostAdder, self).__init__()
    
    def execute(self):
      
        partsCost = self.rotorCost + self.nacelleCost + self.towerCost

        # updated calculations below to account for assembly, transport, overhead and profits
        assemblyCostMultiplier = 0.0 # (4/72)       
        overheadCostMultiplier = 0.0 # (24/72)       
        profitMultiplier = 0.0       
        transportMultiplier = 0.0
        
        self.cost = (1 + transportMultiplier + profitMultiplier) * ((1+overheadCostMultiplier+assemblyCostMultiplier)*partsCost)
        
        # derivatives
        d_cost_d_rotorCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_nacelleCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)
        d_cost_d_towerCost = (1 + transportMultiplier + profitMultiplier) * (1+overheadCostMultiplier+assemblyCostMultiplier)

        if self.offshore:
            self.cost *= 1.1

            # derivatives
            d_cost_d_rotorCost *= 1.1
            d_cost_d_nacelleCost *= 1.1
            d_cost_d_towerCost *= 1.1
        
        # Jacobian
        self.J = np.array([[d_cost_d_rotorCost, d_cost_d_nacelleCost, d_cost_d_towerCost]])

    def provideJ(self):

        input_keys = ['rotorCost', 'nacelleCost', 'towerCost']
        output_keys = ['cost']

        self.derivatives.set_first_derivative(input_keys, output_keys, self.J)
        
#-------------------------------------------------------------------------------       

def example():

    # simple test of module
    
    ppi.ref_yr   = 2002
    ppi.ref_mon  = 9

    turbine = Turbine_CostSE()

    turbine.bladeMass = 17650.67  # inline with the windpact estimates
    turbine.hubMass = 31644.5
    turbine.pitchSystemMass = 17004.0
    turbine.spinnerMass = 1810.5
    turbine.lowSpeedShaftMass = 31257.3
    #bearingsMass = 9731.41
    turbine.mainBearingMass = 9731.41 / 2
    turbine.secondBearingMass = 9731.41 / 2
    turbine.gearboxMass = 30237.60
    turbine.highSpeedSideMass = 1492.45
    turbine.generatorMass = 16699.85
    turbine.bedplateMass = 93090.6
    turbine.yawSystemMass = 11878.24
    turbine.towerMass = 434559.0
    turbine.machineRating = 5000.0
    turbine.advanced = True
    turbine.bladeNumber = 3
    turbine.drivetrainDesign = 1
    turbine.crane = True
    turbine.offshore = True
    turbine.curr_yr = 2009
    turbine.curr_mon =  12

    turbine.run()
    
    print "Turbine cost is ${0:.2f} USD".format(turbine.cost) # $5350414.10
    print
    print "Overall rotor cost with 3 advanced blades is ${0:.2f} USD".format(turbine.rotorCostSE.cost)
    print "Hub cost is ${0:.2f} USD".format(turbine.rotorCostSE.hubSystemCost.hubCost.cost)   # $175513.50
    print "Pitch cost is ${0:.2f} USD".format(turbine.rotorCostSE.hubSystemCost.pitchSystemCost.cost)  # $535075.0
    print "Spinner cost is ${0:.2f} USD".format(turbine.rotorCostSE.hubSystemCost.spinnerCost.cost)  # $10509.00
    print
    print "Overall nacelle cost is ${0:.2f} USD".format(turbine.nacelleCostSE.cost) # $2884227.08
    print "LSS cost is ${0:.2f} USD".format(turbine.nacelleCostSE.lowSpeedShaftCost.cost) # $183363.52
    print "Main bearings cost is ${0:.2f} USD".format(turbine.nacelleCostSE.bearingsCost.cost) # $56660.71
    print "Gearbox cost is ${0:.2f} USD".format(turbine.nacelleCostSE.gearboxCost.cost) # $648030.18
    print "HSS cost is ${0:.2f} USD".format(turbine.nacelleCostSE.highSpeedSideCost.cost) # $15218.20
    print "Generator cost is ${0:.2f} USD".format(turbine.nacelleCostSE.generatorCost.cost) # $435157.75
    print "Bedplate cost is ${0:.2f} USD".format(turbine.nacelleCostSE.bedplateCost.cost)
    print "Yaw system cost is ${0:.2f} USD".format(turbine.nacelleCostSE.yawSystemCost.cost) # $137609.38
    print
    print "Tower cost is ${0:.2f} USD".format(turbine.towerCostSE.cost) # $987180.30 

if __name__ == "__main__":  

    example()